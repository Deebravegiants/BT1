# [M] UpdateInProgress only checked in a limited number of situations

## Summary
Severity: Medium
Contest weight: 0.0541
Dataset id: 9810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
UpdateInProgress is only checked in a limited number of situations: only during "Add-To-Queue", which is send in Borrow(), Transfer() and Redeem(). However the updates are powerful and can perform an arbitrary action on all oTokens. Such an update could influence all actions.

## Recommendation
Consider checking UpdateInProgress for all actions. Also consider adding a check for UpdateInProgress in the function to handle "Check-Queue-For".
