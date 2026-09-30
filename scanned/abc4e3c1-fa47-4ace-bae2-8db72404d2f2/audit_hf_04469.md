# [M] M-11 | setPerpVault Lacks Validation

## Summary
Severity: Medium
Contest weight: 0.0638
Dataset id: 21965
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
setPerpVault() will initialize perpVault, and then will revert anytime it is called again. If a user monitors deployment and calls setPerpVault(), they will be able to set perpVault. This will give a user control over execution flow for numerous function calls, if not dealt with. You could redeploy the contracts again, but you would be at risk of the same attack repeating itself.

## Recommendation
Make setPerpVault() an access controlled function.
