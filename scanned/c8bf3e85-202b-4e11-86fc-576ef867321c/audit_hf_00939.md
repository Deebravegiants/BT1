# [H] H-1 Farming can be deactivated by accident

## Summary
Severity: High
Contest weight: 0.0902
Dataset id: 2900
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current check for farming deactivation can be triggered by accident if tick hasn't changed during the swap and zeroToOne is false EternalVirtualPool.sol#L131-L134. This action will disconnect farming from the pool and will affect incentive distribution for users.

## Recommendation
We recommend using this check EternalVirtualPool.sol#L137-L141 before setting the deactive state to the virtual pool.
