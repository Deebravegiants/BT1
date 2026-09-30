# [M] M-2 Borrowing beyond MaximumLTV

## Summary
Severity: Medium
Contest weight: 0.0635
Dataset id: 9910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LendingPool.borrow() has a limit up to TypeofLTV.MaximumLTV (set at 80% in the project tests). However, LendingPool.withdraw() allows withdrawals up to TypeofLTV.LiquidationThreshold (set at 90% in the tests). An attacker could call borrow() + withdraw() in a single transaction to effectively borrow up to TypeofLTV.LiquidationThreshold, bypassing the MaximumLTV limit.

## Recommendation
We recommend using the same LTV threshold for both borrow() and withdraw().
