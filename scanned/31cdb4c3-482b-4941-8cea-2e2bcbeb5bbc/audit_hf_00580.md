# [H] H-06 | Owner's Initial GMX Not Updated When Matching

## Summary
Severity: High
Contest weight: 0.2561
Dataset id: 2042
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the matchWithdrawRequest function of the ExitVault contract, there is an accounting error when the matcher is the owner. While the owner's gmxStream.shares are increased when matching a withdrawal request, their ownerInitialGMX value is not updated accordingly. This creates a mismatch between the owner's actual shares and their recorded initial GMX amount. The issue occurs because: 1. When matching a withdrawal request, the owner receives additional shares through matcherInfo.gmxStream.shares = totalShares 2. However, ownerInitialGMX is only decremented when the owner is the staker (_staker == s.owner). There is no corresponding increment when the owner is the matcher This mismatch leads to the following issues: • The owner can only request withdrawals up to their ownerInitialGMX amount • Additional shares obtained through matching become effectively locked • The owner's withdrawal capacity doesn't reflect their true position • The discrepancy grows with each matched withdrawal request The same can be said for the owner's initial GLP.

## Recommendation
Add a check in the matchWithdrawRequest function to update ownerInitialGMX when the matcher is the owner. After updating matcher shares, add: if (msg.sender == s.owner) s.ownerInitialGMX = totalShares; Repeat this pattern for GLP.
