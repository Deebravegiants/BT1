# [M] M-09 | Rewards Not Updated Prior To Fee Change

## Summary
Severity: Medium
Contest weight: 0.0606
Dataset id: 22215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Owner can set a new protocol fee via setProtocolFee. However, because rewards are not updated prior to the fee change, the new fee will apply to previously accrued rewards. For example, 100 PEAS in rewards were accrued since the last update. Fees are increased from 1 to 2%. An additional 1% of fees are unjustly applied to the accrued rewards.

## Recommendation
In setProtocolFee, call _processRewardsToPodLp before setting protocolFee to the new fee.
