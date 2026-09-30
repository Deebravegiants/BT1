# [M] Round-off errors during ratioBPs splits will

## Summary
Severity: Medium
Contest weight: 0.7606
Dataset id: 22804
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Per the contest README:
We need to monitor specially that there is no set of inputs that allows a transaction to succeed if the balance of the contracts involved in after the transaction is greater than before the transaction. This means that we want that always balance before trading is equal to balance after trading for all contracts for all tokens.
language that indicates the codebase's restrictions and/or expected functionality. Issues that break these statements, irrespective of whether the impact is low/unknown, will be assigned Medium severity.
We show that for multi-hop trades with valid inputs, the ratioBPS round-off errors for realistic UniV2/UniV3/Balancer swaps will almost always leave the contract with some dust amounts of middle tokens.
The contract Maradona (and Messi but permissioned) allows performing multi-hop trades, where each hop can be split across multiple markets with different ratio.
From the second hop onwards, the operation's amountIn is overriden by the previous hop's output, multiplied by the ratio intended for this particular swap market.
dit-v1/contracts/Paymaster/Maradona.sol#L389
```solidity
if (op.useContractFunds) {
    op.amountIn = (prevCumOutputAmount * ratioBPs) / 10000;
}
```
However, most (if not almost all) of the time, a swap on UniV2/UniV3/Balancer does not return an amount out perfectly divisible by 10000, which causes truncation of at most 0.9999 wei in the above division. If the hop contains two or more swaps, the truncation will total to 1 wei or more that remains in the contract, scaled by the number of operations for that hop.
Because the amountIn is always calculated that way, and the round-off amounts are never swept, the round-off amounts remains in the contract.
• Breaks invariant defined by the protocol, that the contract should not hold any balance after trades
– Specifically, Gemini USD has only 2 decimals. Therefore any precision loss may be material if accumulated.

## Proof of Concept
Consider the following trade:
• Op1: ETH ---> WBTC, ratioBPs = 10000, market = Uniswap V2
– This is the first hop, and trades perfectly normal
• Op2: WBTC ---> USDC, ratioBPs = 6666, market = Uniswap V3
• Op3: WBTC ---> USDC, ratioBPs = 3334, market = Balancer
– These two represents the second hop, with two-thirds routed through UniV3, and a third routed towards Balancer
For as long as operation 1 does not return an amount of WBTC perfectly divisible by 10000 (which is almost always the case), there will be some round-off errors in each of operation 2 and 3, resulting in WBTC remainings in the contract.
Coded PoC
We provide a coded PoC to prove that dust amounts will stay in the contract, for a non-perfectly-round output multihop trades
First, modify line 64-65 of MockMarketSpecifyRate to following:
dit-v1/contracts/mock/MockMarketSpecifyRate.sol#L65
```solidity
uint256 amountOut = amountIn*378909/68078010000000000;
```
Then, paste the following test into Maradona.test.ts. The test sets up a trade:
• Hop 1: 1 ETH to WBTC
• Hop 2: The output WBTC, split into 66.66% and 33.34%, to a market with 1:1 exchange rate
```typescript
it.only("PUSH0 PoC - round off ratioBPs leaves funds", async function () {
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
    const middleToken = mockTokens[0];
    const middleTokenAddress = middleToken.target.toString();
    const outputToken = mockTokens[1];
    const outputTokenAddress = outputToken.target.toString();
    // Op Params
    const value = ethers.parseEther("1");
    const opParams: OperationParametersStruct[] = [getEmptyOpParams(), getEmptyOpParams(), getEmptyOpParams()];

    // first hop
    opParams[0].inputToken = ethers.ZeroAddress
    opParams[0].outputToken = middleTokenAddress
    opParams[0].ratioBPs = toBigInt(10000)
    opParams[0].amountIn = value.toString()
    opParams[0].exchangeID = 3
    // second hop, 66.66%
    opParams[1].inputToken = middleTokenAddress
    opParams[1].outputToken = outputTokenAddress
    opParams[1].ratioBPs = toBigInt(6666)
    opParams[1].useContractFunds = true
    opParams[1].exchangeID = 1
    // second hop, 33.34%
    opParams[2].inputToken = middleTokenAddress
    opParams[2].outputToken = outputTokenAddress
    opParams[2].ratioBPs = toBigInt(3334)
    opParams[2].useContractFunds = true
    opParams[2].exchangeID = 1
    // asserts all initial balances are zero
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))

    expect(await middleToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    // now trade
    const tx = await maradona.connect(trader).takeTokensAndTrade(
        opParams,
        "0",
        owner.address,
        traderAddress,
        ethers.ZeroAddress,
        {
            value: value,
        }
    )
    const rx = await tx.wait();
    // assert that the middle token's balance is greater than zero
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))

    expect(await middleToken.balanceOf(maradona.target)).to.be.greaterThan(toBigInt(0))

    expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    // log it out
    console.log("Output token balance of trader:", await outputToken.balanceOf(traderAddress))

    console.log("Middle token balance of Maradona:", await middleToken.balanceOf(maradona.target))

});
```
Run the test with make tests/Maradona, and the test will give a log:
Proving that indeed 1 wei gets stuck in the contract. A round-off amount of N × 1 wei can be achieved for each hop that requires N swaps.

## Recommendation
As soon as the ratioBPs reaches 10000, op.amountIn should be set to the remaining amount:
```solidity
if (op.useContractFunds) {
    op.amountIn = (prevCumOutputAmount * ratioBPs) / 10000;
    if (cumRatio + ratioBPs == 10000) {
        op.amountIn = prevCumOutputAmount - cumOutputAmount;
    }
}
```
