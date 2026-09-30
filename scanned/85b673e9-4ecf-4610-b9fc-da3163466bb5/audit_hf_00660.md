# [M] M-08 | Event Emitted With Incorrect Values

## Summary
Severity: Medium
Contest weight: 0.0438
Dataset id: 2196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MainAndStrategyFundsSettled event’s first parameter should represent the mainAssets amount. However, it is currently emitted with the periodId. Since the protocol’s backend heavily relies on event emissions, this issue may cause incorrect operations on the backend.

## Recommendation
Update the event.
