# [H] ConnextHandler executeFailedWithUpdatedArgs(...) reentrancy allowedCaller can steal all ConnextHandler tokens

## Summary
Severity: High
Contest weight: 0.0885
Dataset id: 8210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In executeFailedWithUpdatedArgs(...), the allowedCaller can steal all assets available on the ConnextHandler by calling executeFailedWithUpdatedArgs(...) again after the xBundle(...) call. This can be mitigated also by adding the nonReentrant modifier to xBundle(...).

## Recommendation
Write txn.executed = true; before the try/catch call and rewrite txn.executed = false if it fails.
