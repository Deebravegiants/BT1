# [M] M-21 | Reallocate Can Leave Assets In Contract

## Summary
Severity: Medium
Contest weight: 0.0499
Dataset id: 2555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reallocate function will move funds from one pool to another one. However, there is no check that the total amount of assets redeemed as effectively deposited into the new pools. Assets not deposited will not earn interest, so SuperPool user's earnings will be affected.

## Recommendation
Verify that the total amount redeemed from pools matches the total amount deposited.
