# [M] Use safeTransfer and safeTransferFrom

## Summary
Severity: Medium
Contest weight: 0.0551
Dataset id: 6371
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In BalanceTrackerFixedPriceNative and BalanceTrackerFixedPriceToken, the IToken interface has been used that defines transfer and transferFrom functions to return a bool.
1. Not all tokens conform to this interface when transferring amounts.
2. The returned bool value has not been checked.

## Recommendation
Use the safer implementation of token transfers to rule out the above issues. Look at OpenZeppelin's implementation of SafeERC20.
