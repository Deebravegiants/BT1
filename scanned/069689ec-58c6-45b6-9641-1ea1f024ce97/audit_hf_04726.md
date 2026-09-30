# [M] Penrose::_depositFeesToTwTap can unexpect-

## Summary
Severity: Medium
Contest weight: 0.1184
Dataset id: 22538
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_depositFeesToTwTap computes the amount of fees withdrawn after having it withdrawn. There may be a difference with actual fees withdrawn which could cause the function to revert unexpectedly
We can see the fees being withdrawn here, but instead of using the amount withdrawn, the amount is recomputed from shares here
This can be problematic if during first call the fee amount is rounded down, but after being withdrawn, it is not being rounded down
Example
• before withdrawal:
base: 7 elastic: 13 share: 2
amount withdrawn: 13*2/7 = 3 shares deducted = 2
• after withdrawal:
base: 5 elastic: 10 share: 2
amount computed: 10*2/5 = 4
The transfer reverts because only 3 has been withdrawn
The call will withdraw unexpectedly in some cases, dosing fees withdrawal

## Recommendation
Compute the amount of fees which will be withdrawn before making the actual withdrawal in _depositFeesToTwTap
