# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.0519
Dataset id: 8426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In setAuction() we have couple of params that require a proper validation in case of a error from the side of the owner or a malicious/compromised one. You have perfectly validated the input of the min param but the same is lacking for max & duration which can be problematic in some cases.

## Recommendation
Write reasonable checks for those two params in order to avoid further issues.
