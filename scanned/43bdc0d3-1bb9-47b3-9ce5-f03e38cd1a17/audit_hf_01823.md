# [M] feeRate validations are insufficient

## Summary
Severity: Medium
Contest weight: 0.0602
Dataset id: 10120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are two problems with the feeRate property in FeeBase. There are validations in _setRewardFeeRate that are missing in initializeFeeBase, so the feeRate can initially be set to any uint256 number. The pool admin can set the fee to 100% and steal all new rewards from users.

## Recommendation
Make sure to implement the same validations in initializeFeeBase that are in _setRewardFeeRate (you can remove the >= 0 validation, as it is always true for a uint256 value). Also make the max fee to be a smaller percentage, for example 10%.
