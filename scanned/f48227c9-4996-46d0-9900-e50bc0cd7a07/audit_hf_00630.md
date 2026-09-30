# [M] M-07 | No Post-Deposit Safety Check In depositCollateral Function

## Summary
Severity: Medium
Contest weight: 0.0671
Dataset id: 2131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The depositCollateral function allows users to add collateral to an existing position but fails to verify whether the position is then sufficiently collateralized or safe from liquidation immediately afterward. A user might deposit too little collateral, resulting in a position that still remains under collateralized and can be liquidated right away.

## Recommendation
Include a safety check after the collateral deposit to confirm that the position’s margin requirements are now satisfied. If the position is still unsafe, revert the transaction.
