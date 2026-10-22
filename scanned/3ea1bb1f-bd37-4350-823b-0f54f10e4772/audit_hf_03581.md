# [M] ML-4 | findLargestPosition Exposes Liquidator to Unnecessary Slippage

## Summary
Severity: Medium
Contest weight: 0.0823
Dataset id: 19560
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquidate function, a liquidator is forced to liquidate from the asset with the largest notional value. This approach can result in less profit for the liquidator, especially when the position with the highest notional value involves a less liquid pool, this is because smaller pools experience more slippage during swaps. This limitation makes positions with certain assets as their largest holding less attractive to liquidate due to reduced profits, increasing the likelihood of incurring bad debt.

## Recommendation
Allow liquidators to choose which asset they want to liquidate.
