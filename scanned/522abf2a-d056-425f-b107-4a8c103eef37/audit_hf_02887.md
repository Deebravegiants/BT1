# [M] GLOBAL-1 | Poor Practices

## Summary
Severity: Medium
Contest weight: 0.0729
Dataset id: 16187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the contracts there are myriad instances of:
Lack of camelcase
Unnecessary local variables which waste gas
Redundant boolean checks e.g. == true
Typos in the comments
Unnecessary for-loops which waste gas and enable DoS
Ineﬃcient computations e.g. feeBalance -= feeBalance
Many functions can be declared external

## Recommendation
Use camelcase throughout the contracts, remove redundant and unnecessary local variables, do not
perform redundant boolean checks, revise comments, refactor operations to avoid unnecessary
for-loops, avoid ineﬃcient computations e.g. use feeBalance = 0, declare all functions that are not
called within the contracts external rather than public
