# [M] GLOBAL-1 | Liquidations When Features Disabled

## Summary
Severity: Medium
Contest weight: 0.0548
Dataset id: 18503
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for a state to arise where liquidations are enabled but other order types are disabled.
For example, increase orders can be disabled and a user is unable to add collateral to their position.
Fees will accumulate until a user’s position is liquidatable which leads to loss of funds.

## Recommendation
Consider disallowing liquidations when a user is unable to adjust their order due to a feature being
disabled.
