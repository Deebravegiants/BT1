# [M] M-07 | setFundingRate Unexpectedly Changes Funding

## Summary
Severity: Medium
Contest weight: 0.0746
Dataset id: 21448
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setFundingRate function allows a permissioned address to update the maxFundingRate, which potentially caps the existing funding rate for pending funding fees. This action would affect funding fees that have accumulated in the past causing unexpected funding changes for users, which could ultimately lead to accounts being subject to unexpected liquidation as a result of receiving less funding fees than expected.

## Recommendation
Update the funding state before updating the maxFundingRate similar to the setPositionImpactDistributionRate function distributes the impact pool.
