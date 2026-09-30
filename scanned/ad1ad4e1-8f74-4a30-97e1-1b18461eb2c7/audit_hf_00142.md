# [M] Wrong calculation on `_collectRentAction`

## Summary
Severity: Medium
Contest weight: 0.0823
Dataset id: 554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The method `_collectRentAction` contains the [following code](https://github.com/code-423n4/2021-06-realitycards-findings/issues/122#issue-922787380):

in case 6, it is doing:
    
    _refundTime = block.timestamp - marketLockingTime;

instead of:
    
    _refundTime = _timeUserForeclosed - marketLockingTime;

This could lead to funds being drained by the miscalculation.

This is a really great find!!

Fix implemented [here](https://github.com/RealityCards/RealityCards-Contracts/commit/457cc782c196e34b3b9d95a2d2c7b52ee6c17f2d)

## Recommendation
No recommendation
