# [M] M-07 | Associate Debt Incompatible With Multiple Pools

## Summary
Severity: Medium
Contest weight: 0.0787
Dataset id: 2572
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AssociateDebtModule allows a market to associate debt with a specific position. Based on the current implementation with the Legacy Market, it makes the assumption that all debt will be distributed to one pool. However, if there are multiple pools backing the market, then the debt is proportionally distributed to the pools and AssociateDebtModule would incorrectly associate all the debt to the user in one pool.

## Recommendation
If a market is connected to multiple pools, 1) associate the correct proportion of debt to the user in each pool/vault that the user is in, 2) perform a debt correction for pools which have received some of the debt.
