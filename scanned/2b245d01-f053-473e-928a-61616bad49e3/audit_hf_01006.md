# [H] H-2 Hashﬂow RFQ-integration

## Summary
Severity: High
Contest weight: 0.5384
Dataset id: 3411
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since we receive HashflowQuote before the call occurred, the information at the time of the transaction may not be up to date.
In that case, due to this code:
```solidity
if (amount > quote.maxBaseTokenAmount) {
    emit AmountExceedsQuote(amount, quote.maxBaseTokenAmount);
    quote.effectiveBaseTokenAmount = quote.maxBaseTokenAmount;
} else {
    quote.effectiveBaseTokenAmount = amount;
}
```
part of the money may remain with the SwapExecutor.
• HashﬂowHelper.sol#L24

## Recommendation
We recommend adding a revert if the input amount is not actual.
