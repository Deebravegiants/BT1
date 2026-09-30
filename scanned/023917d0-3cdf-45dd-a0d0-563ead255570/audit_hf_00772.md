# [M] M-03 | Updating Fee Values Affects Fees

## Summary
Severity: Medium
Contest weight: 0.0828
Dataset id: 2398
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When setHookFeePercentage() is called, the hook fee percentage will be updated (increased or decreased). An increase in this percentage will cause the user to receive less fees than expected from their already accumulated fees. A user might be checking that they should receive $100 in fees based on swaps already executed, then the admin increases the fee percentage, now the user will only receive $50.

## Recommendation
Implement a fee change functionality that operates based off of the original fee percentage until _retrackPositionFee() is called. This will ensure that the proper percentage is used until the pool is updated. Further, potentially create another function that performs fee checkpointing for multiple positions in a batch.
