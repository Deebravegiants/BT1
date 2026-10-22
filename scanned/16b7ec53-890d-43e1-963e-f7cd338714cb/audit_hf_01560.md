# [M] The system is not fully usable with the Uniswap Widget

## Summary
Severity: Medium
Contest weight: 0.4331
Dataset id: 8346
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
One of the requirements for the protocol is that the system must be fully usable with the Uniswap Widget. However, the following incompatible features have been found:
During the snipe protection period, quotes on buys of the g8keep token might not return the correct amount, and maxSnipeProtectionBuyWithoutPenalty is expected to be used to calculate the maximum amount of tokens that can be bought without penalty. This flow is not supported by the Uniswap Widget.
There is no mention in the documentation about support on fee-on-transfer tokens and, after reviewing the source code of the Uniswap Widget, there has not been found the possibility for the developer to support these tokens.
The only instance of such support in the Uniswap SDK's was found in the v2-sdk router
```solidity
* Whether any of the tokens in the path are fee on transfer tokens, which should use swapXXWithFeeOnTransferTokens
feeOnTransfer?: boolean
const useFeeOnTransfer = Boolean(options.feeOnTransfer)
let methodName: string
let args: (string | string[])[]
let value: string
switch (trade.tradeType) {
    case TradeType.EXACT_INPUT:
        if (etherIn) {
            methodName = useFeeOnTransfer ? 'swapExactETHForTokensSupportingFeeOnTransferTokens' :
```
However, it has not been found how to use this feature in the Uniswap Widget.
As such, using the Uniswap Widget to buy or sell the g8keep token might not work as expected.

## Recommendation
Given that the sniping protection and fees on transfer are essential features of the protocol, it is recommended to use a more flexible alternative to the Uniswap Widget, or build a custom widget using Uniswap's v2-sdk.
