# [M] admin in the Insurance contract can never be set

## Summary
Severity: Medium
Contest weight: 0.0412
Dataset id: 14000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The initialize() function in Insurance.sol does not set admin. As such, it is impossible for the admin to be set as setAdmin() can only be called by the contract's admin.
This makes it impossible for the admin to call coverLoss() should the need arise.

## Recommendation
Consider setting admin in initialize().
