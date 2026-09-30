# [M] M-10 | Period Update Breaks When Batching

## Summary
Severity: Medium
Contest weight: 0.0922
Dataset id: 2198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When updateStrategyFundAssets is called it will iterate through all funds. However given that there is no hard cap on the number of funds the protocol can have and that fund creation will become permissionless it will eventually require multiple iterations to update all the funds. The issue with this is that mainAssetsAfterFees will become much less than its actual value on the second call since it will not take into account mainAssetsAfterFees from the first call. The reduced mainAssetsAfterFees will drastically reduce users share value.

## Recommendation
Modify the updateStrategyFundAssets function so that it can be called multiple times without losing data from previous updateStrategyFundAssets calls.
