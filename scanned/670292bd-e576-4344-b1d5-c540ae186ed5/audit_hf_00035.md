# [C] PORT-2 | Incorrect Approval Prevents Liquidation

## Summary
Severity: Critical
Contest weight: 0.1171
Dataset id: 111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the removeMargin function, before a swap occurs an amount is approved. This is supposed to be the token amount that is being swapped. However the USD value of the token amount is approved instead. This is especially detrimental when a token’s USD value is less than $1 because the approval will be insufficient for the swap causing a revert and making liquidations via removeMargin impossible.

## Recommendation
Approve the token amount that will be swapped instead of the USD amount.
