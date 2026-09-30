# [C] C-06 | RewardDistributor Incompatible With Collaterals

## Summary
Severity: Critical
Contest weight: 0.0956
Dataset id: 22077
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RewardsDistributor.distributeRewards() supports only one collateral type. However, the Perps system loops over multiple collaterals and calls distributeCollateral for each one of them. This operation will fail and will cause the whole transaction to revert which will DOS the perps market liquidation functionality.

## Recommendation
Remove the checks from the RewardDistributor contract
