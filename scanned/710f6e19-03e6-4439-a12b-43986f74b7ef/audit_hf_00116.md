# [M] No default `liquidationThresholdPercent`

## Summary
Severity: Medium
Contest weight: 0.0853
Dataset id: 251
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `IsolatedMarginTrading` contract does not define a default `liquidationThresholdPercent` which means it is set to 0. The `belowMaintenanceThreshold` function uses this value and anyone could be liquidated due to `100 * holdings >= liquidationThresholdPercent * loan = 0` being always true.

Anyone can be liquidated immediately. If the faulty `belowMaintenanceThreshold` function is fixed (see other issue), then nobody could be liquidated which is bad as well.

Recommend setting a default liquidation threshold like in `CrossMarginTrading` contracts.

## Recommendation
No recommendation
