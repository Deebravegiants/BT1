# [M] Allowances Can Be Frontran

## Summary
Severity: Medium
Contest weight: 0.0560
Dataset id: 14206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SubAccounts::setAssetAllowances() and SubAccounts::setSubIdAllowances() set allowances directly rather than increasing or decreasing the allowance. This makes it vulnerable to the classic approve() frontrunning issue where the allowance can be spent twice through frontrunning when the user is attempting to set a new allowance.

## Recommendation
Implement increase and decrease allowance functions.
