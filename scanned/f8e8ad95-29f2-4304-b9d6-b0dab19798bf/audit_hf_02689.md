# [M] Uninitialized WithdrawDelay

## Summary
Severity: Medium
Contest weight: 0.0654
Dataset id: 14546
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdrawDelay value is used in the function claimWithdraw() to calculate the waiting period before operators are able to withdraw their SDCollateral tokens.
However withdrawDelay is uninitialized, so that prior to setWithdrawDelay() being called withdrawDelay will default to zero which results in operators being able to immediately claim their sd collateral tokens.

## Recommendation
The testing team recommends initializing withdrawDelay to a reasonable default value in the initializer.
