# [M] M-06 | Owner Can Bypass UMA Assertion Checks

## Summary
Severity: Medium
Contest weight: 0.0636
Dataset id: 22089
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UmaSettlementModule is a contract which ensures owner submits a valid settlement price. However, the owner can change the address of the oracle at any time, and the address does not have to be a legitimate oracle. The owner can call updateMarket, change the optimisticOracleV3 address to themselves, and then call assertionResolvedCallback() to accept a malicious price.

## Recommendation
Consider only allowing oracle updates when the epoch has not ended.
