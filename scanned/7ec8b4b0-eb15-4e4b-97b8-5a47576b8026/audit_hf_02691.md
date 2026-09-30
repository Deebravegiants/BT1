# [M] Non-Reentrant Modifier Conflict

## Summary
Severity: Medium
Contest weight: 0.0502
Dataset id: 14553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the PermissionlessNodeRegistry contract, the function addValidatorKeys() is marked with two nonReentrant modifiers.
This double application of the nonReentrant modifier can lead to unexpected behaviour, causing the function to revert due to the reentrancy guard.

## Recommendation
Remove the redundant modifier to prevent unwarranted reverts and align with standard smart contract practices.
