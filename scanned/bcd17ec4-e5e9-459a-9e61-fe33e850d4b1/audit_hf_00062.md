# [M] M-01 | Imbalance Does Not Count Funding

## Summary
Severity: Medium
Contest weight: 0.1325
Dataset id: 138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While initiating a request to open a position the tradingExpo used to compute the new positions predicted exposure is based on a longTradingExpoWithFunding which includes the funding up until the current block.timestamp. However the imbalance validations that follow, and the imbalance validations throughout the codebase use the current vault and long balances which ignore the funding accrued in the timeframe from the lastUpdateTime until the current block.timestamp. Therefore there is an immediate contradiction in the imbalance validation during the initiation of an update request. The position exposure includes the latest funding, while the aggregate balances do not. Furthermore, the imbalance validations for all actions cannot be accurately validated against the latest funding changes which have yet to be stored.

## Recommendation
Consider accounting for the funding at the latest timestamp in the imbalance validation functions throughout the codebase. Furthermore, consider if the latest unrecorded funding should be taken into account when triggering the rebalancer.
