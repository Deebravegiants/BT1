# [M] GG-1 | Unable to Emergency Withdraw

## Summary
Severity: Medium
Contest weight: 0.0536
Dataset id: 4083
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to require(block.timestamp >= user.stakeUntil, "Locked") in emergencyWithdraw, if a user has LP tokens that are not locked alongside LP tokens that are indeed locked, the user would have to wait until their locked LP tokens become unlocked before they can emergencyWithdraw.

## Recommendation
If this is intended behavior, keep as is. Otherwise, refactor emergencyWithdraw such that users may withdraw their unlocked positions.
