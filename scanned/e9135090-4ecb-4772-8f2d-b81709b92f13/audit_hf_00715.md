# [M] M-09 | Pending Fees Altered By setMarketConﬁguration

## Summary
Severity: Medium
Contest weight: 0.0881
Dataset id: 2266
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the setMarketConﬁguration function is called, the admin can change the utilizationBreakpointPercent, lowUtilizationSlopePercent, and highUtilizationSlopePercent. Once these values are adjusted, all pending utilization fees will be updated according to the new slope, rather than the slope that was initially set when the fees were accruing. This adjustment will result in a sudden increase in fees owed by users, potentially putting them in a liquidatable state due to the past utilization incorrectly increasing based on the new slope.

## Recommendation
Consider updating the pending utilization fees in the setMarketConﬁguration function.
