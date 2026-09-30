# [M] M-05 | Missing Check In delegateCollateral

## Summary
Severity: Medium
Contest weight: 0.0514
Dataset id: 2570
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The delegateCollateral function does not check if the given vault can be liquidated. Therefore it is possible that an LP delegates to a vault and is instantly liquidated. This is a general issue in the delegateCollateral function, that can also occur when migrating from V2 to V3.

## Recommendation
Add a check in the delegateCollateral function to ensure that the vault can not be liquidated.
