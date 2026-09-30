# [M] M-01 | SP Deposits Are Not Refunded

## Summary
Severity: Medium
Contest weight: 0.0765
Dataset id: 2218
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the handleOpFromVault function of ProtocolVaultLedger, whenever a deposit operation targets a strategy provider (spId) that is not marked as allowed (isAllowedStrategyProvider[spId] = false), the contract simply emits an event and returns. This silent return means that the deposited tokens, already locked on the ProtocolVault side are not refunded to the strategy depositor. As a result, funds end up stuck, creating a loss scenario for the depositor.

## Recommendation
Consider incorporating a refund logic for the deposited assets to cover this edge case.
