# [M] Payback can be DoSed in the BorrowingVault, may be profitable for liquidators

## Summary
Severity: Medium
Contest weight: 0.0679
Dataset id: 8242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The borrowing vault enables anyone to payback the debt of another user. Thus, attackers can frontrun a user payback transaction, payback 1 wei and stop users from paying back their debts. This would make sense for liquidators, who are incentivized to do this to liquidate users.

## Recommendation
There are 2 alternatives:
- Instead of reverting if the payback is bigger than the maximum, limit it to the maximum.
- Only enable the user to payback its debt.
