# [M] QUEUE-3 | Malicious User Can Push Deposits

## Summary
Severity: Medium
Contest weight: 0.0504
Dataset id: 135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user can prevent the epoch from rolling over by calling addLiquidity with multiple 1 wei positions past the limitProcess. This will cause the admin to have to execute multiple transactions to process the queue and expend a potentially significant amount of gas.

## Recommendation
Add a minimum deposit amount and consider adding a deposit fee to dissuade these manipulations
