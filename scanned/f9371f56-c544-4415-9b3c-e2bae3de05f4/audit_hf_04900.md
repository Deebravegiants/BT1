# [H] ERC20-only trades can be done on Maradona

## Summary
Severity: High
Contest weight: 0.6311
Dataset id: 22816
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Per the Maradona code: dit-v1/contracts/Paymaster/Maradona.sol#L283 require(ops[0].inputToken == address(0), "Maradona: first operation must be from eth"); Thus it can be inferred that Maradona should only support trades beginning with ETH. Per the contest README: Q: Please discuss any design choices you made. The idea is to chain swaps one after the other so: we always swap with tokens inside the contract (e.g. you can't do wETH->USDC and DAI->wBTC in the same transaction), and the check for minAmountOut is only done in the last output overriding anything in between. Also, we decided to override every minAmountOut check for each hop except for the last one. Any vulnerability related to this should be reported as an issue. We show that it is still possible do trades similar to WETH->USDC and DAI->wBTC in the same transaction. We also extend on this fact, and show a way to perform arbitrary ERC20 trades at a cost of dust ETH amounts only using the Maradona contract. This attack also has a side effect of bypassing protocol fees. In the following branch: dit-v1/contracts/Paymaster/Maradona.sol#L377-L384 // Check if last start address is different that the current start address // If it is, we reset the cumRatio and cumOutputAmount if (i > 0 && op.inputToken != lastAddress) { require(cumRatio == 10000, "Maradona: cumRatio is not 10000"); cumRatio = 0; prevCumOutputAmount = cumOutputAmount; cumOutputAmount = 0; canBeFromEth = false; mustUseContractFunds = true; } If the new input token is different from the old input token, then a new split begins, with the previous output amount. However, there is no validation that the new input token matches the old output token. Therefore any trades similar to ETH->USDC and DAI->wBTC in the same operation, that should not have been supported, is now possible. There is still a restriction that the code takes the USDC output amount as the first trade to be DAI's input amount for the second trade (see prevCumOutputAmount = cumOutputAmount; and the line below) dit-v1/contracts/Paymaster/Maradona.sol#L389-L391 if (op.useContractFunds) { the second hop onwards, overwrite amountIn } However, by utilizing Balancer's architecture, we show that it is possible to set up a fake Balancer pool and a fake ERC20 token, to trick Maradona contract into using our supplied amount of DAI for the second operation. • Breaks protocol invariant, that Maradona is supposed to work with trades starting with ETH only • Breaks protocol invariant, that a non-chain trade as shown in the README example should not work • Breaks protocol invariant, that balances should not be left in the contract after a trade • Renders the Messi contract obsolete • Bypassing of protocol fees and all other types of fees

## Proof of Concept
Our goal is to perform a swap of WBTC --> USDC using the Maradona contract, using the following starting materials: • A dust amount of ETH (10000 wei is sufficient) • The amount of WBTC we want to input, let's say 1 WBTC. • An arbitrary ERC20 token that we created that does not need a value. We will call this PUSH1 token Balancer’s architecture consists of a permissionless Vault, such that any Pool math can be plugged into the Vault to use as its own exchange. the Vault is agnostic to pool math and can accommodate any system that satisfies a few requirements. Anyone who comes up with a novel idea for a swapping system can make a custom pool plugged directly into Balancer's existing liquidity instead of needing to build their own Decentralized Exchange. The full steps to trade ERC20 using the given input, are as follow: 1. Set up a fake Balancer pool, such that the logic of the pool is "when ETH is traded as input into the pool, transfer any amount of PUSH1 token to the trader". The amount of PUSH1 tokens out can be supplied by us (e.g. through a permissioned function). • Of course, mint enough PUSH1 tokens to the pool 2. Transfer 1 WBTC directly into the pool 3. Perform the following swap with two operations: • Op 1: ETH --> PUSH1. Amount in = 10000 wei, useContractFunds = false, ratioBps = 10000 • Op 2: WBTC --> USDC. Amount in = 1 WBTC, useContractFunds = true, ratioBps = 10000 • Fee token = ETH • The Balancer pool is set up so that exactly 1e8 PUSH1 tokens is returned After the swap, the attacker loses 10000 wei of ETH (which can still be retrieved from the Balancer pool), and leave behind in the contract 1e8 PUSH1 tokens that has no value. The WBTC is swapped to USDC, but fees are only charged on the tiny amount of 10000 wei of ETH. Another way to perform the attack is to make a custom PUSH1 token with a transfer hook (which ERC20 supports). The 1 WBTC is not transferred into the contract at step 2, but rather when the PUSH1 token is transferred into Maradona (when completing the first trade). This guarantees that there is no risk of someone stealing the WBTC at step 2. Coded PoC We prove that the operation succeeds through a coded PoC. The PoC: • Transfers middleToken into the contract directly • Sets up two trades: ETH --> fakeToken, then middleToken --> outputToken • Shows through console logs that the trade is successful, and the trader does indeed receive outputToken
```js
it.only("PUSH0 PoC - ERC20 only", async function () {
// Load fixture elements
const {signers, maradona, mockMarkets, mockTokens} = await loadFixture(deployFixture);
// User stuff
const owner = signers[0];
const users = signers.slice(1);
const sponsor = users[0];
const traders = users.slice(1);
const trader = traders[0];
const traderAddress = trader.address.toLowerCase();
// update sponsor
await maradona.connect(owner).updateCollector(sponsor.address)
// Token stuff
const fakeToken = mockTokens[1];
const fakeTokenAddress = mockTokens[1].target.toString();
const realInputToken = mockTokens[2];
const realInputTokenAddress = realInputToken.target.toString();
const outputToken = mockTokens[3];
const outputTokenAddress = outputToken.target.toString();
// two operations:
// Op1: ETH ---> fake token, amount = 1 ETH, bps = 10000
// Op2: real input token --> output token, amount = any, bps = 10000
// Fee token: ETH
const valueONE = ethers.parseEther("1");
const feeBps = toBigInt(5);
const feeValue = toBigInt(2) * valueONE * feeBps / toBigInt(10000)
const opParams: OperationParametersStruct[] = [getEmptyOpParams(), getEmptyOpParams()];
opParams[0].inputToken = ethers.ZeroAddress
opParams[0].outputToken = fakeTokenAddress
opParams[0].ratioBPs = toBigInt(10000)
opParams[0].amountIn = valueONE.toString()
opParams[0].exchangeID = 1
opParams[1].inputToken = realInputTokenAddress
opParams[1].outputToken = outputTokenAddress
opParams[1].ratioBPs = toBigInt(1)
opParams[1].useContractFunds = true;
opParams[1].amountIn = 0
opParams[1].exchangeID = 1
// trade and test!
expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))
expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
// mint tokens for trader first
await realInputToken.connect(owner).mint(traderAddress, valueONE)
// transfer directly to the market
await realInputToken.connect(trader).transfer(maradona.target, valueONE)
// now trade
const tx = await maradona.connect(trader).takeTokensAndTrade(
opParams,
"0",
owner.address,
traderAddress,
ethers.ZeroAddress,
{
value: valueONE,
}
)
const rx = await tx.wait();
const txGas = rx ? rx.cumulativeGasUsed * rx.gasPrice : toBigInt(0);
expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))
expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
console.log("Traders's output token balance:", await outputToken.balanceOf(traderAddress))
});
```
Run the test with make tests/Maradona, the test log shows:

## Recommendation
The root cause is that there is no validation that, for each hop/split, the new input token is the same as the previous output token. Add such validation in the following if branch: dit-v1/contracts/Paymaster/Maradona.sol#L377-L384 if (i > 0 && op.inputToken != lastAddress) { require(cumRatio == 10000, "Maradona: cumRatio is not 10000"); require(op.inputToken == swapOps[i-1].outputToken, "Token mismatch"); cumRatio = 0; prevCumOutputAmount = cumOutputAmount; cumOutputAmount = 0; canBeFromEth = false; mustUseContractFunds = true; } The same happens with the Messi contract, albeit with less impact since it is permissioned (the only impact is funds stuck in the contract)
