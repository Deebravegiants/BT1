# [M] M-16 | WithdrawUsd May Try To Withdraw 0

## Summary
Severity: Medium
Contest weight: 0.0792
Dataset id: 2116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FacetPositionAccount.withdrawUsd calculates the amount of payingCollateral to withdraw from the user's account by calling _withdrawFromAccount. It's possible for payingCollateral to result in 0 because of rounding if the user has small amount of collateral (may happen naturally by realizing negative PnL). If this happens, the whole transaction will revert since _withdrawFromAccount fails if the amount to be withdrawn is 0. In result, the user won't be able to use withdrawUsd.

## Recommendation
Skip the current iteration if the amount of collateral to be withdrawn is 0.
