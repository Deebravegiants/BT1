# [M] M-10 | Incorrect pendingBalanceVault Correction

## Summary
Severity: Medium
Contest weight: 0.0812
Dataset id: 167
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _removeBlockedPendingAction function the _pendingBalanceVault is corrected by computing the withdrawal amount without accounting for fees.
However upon the initiation of the withdrawal the _pendingBalanceVault was decremented by the withdrawal amount less fees.
As a result when a withdrawal action is removed with the _removeBlockedPendingAction function using cleanup as true the _pendingBalanceVault experiences an invalid net increase by the withdrawal fee amount.

## Recommendation
Correct the _pendingBalanceVault by the withdrawal amount accounting for fees in the _removeBlockedPendingAction function.
