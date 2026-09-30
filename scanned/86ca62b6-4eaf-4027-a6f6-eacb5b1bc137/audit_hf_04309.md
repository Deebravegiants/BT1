# [H] H-06 | Migration Cannot Be Done

## Summary
Severity: High
Contest weight: 0.7318
Dataset id: 21459
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the migration process, the owner will construct the initial distribution of spot and credits and it will be done with allocate function. This can only be called before the pool is launched, and the pool will be deployed later.
Users might have both spot and credit to be distributed. But a user can also have only spot or only credit. However, the check that ensures the allocation is not empty is incorrect, and the allocate function will revert if a user has only spot or only credit.
The whole migration process will be disrupted even if just one user has only spot or only credit.

## Recommendation
Change this line
```solidity
if (_spot[i] == 0 || _collateral[i] == 0) revert InvalidAllocation();
```
to this:
```solidity
if (_spot[i] == 0 && _collateral[i] == 0) revert InvalidAllocation();
```
