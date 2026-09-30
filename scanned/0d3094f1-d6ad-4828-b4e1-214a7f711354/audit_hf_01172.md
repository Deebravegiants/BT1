# [M] Set owner unable to update configuration when insolvent

## Summary
Severity: Medium
Contest weight: 0.0964
Dataset id: 5025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Set owner may only update the configuration in a manner that does not cause the utilization of any market to rise to and over 100%. This would create insolvent markets, meaning a market would not have enough collateral to cover its claims when triggered.
But the insolvency of markets can naturally occur from the fact that Sets may choose to use leverage, i.e., use the same collateral to cover multiple markets. In that case, a Set owner would now be unable to apply any changes to the configuration until enough new collateral has been supplied to ensure the solvency of all markets.

## Recommendation
The business logic should be adjusted to allow Set owners to still be able to update the configuration in these extreme cases.
