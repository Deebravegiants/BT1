# [C] C-01 | Anyone Can Trigger Limit Orders

## Summary
Severity: Critical
Contest weight: 0.1089
Dataset id: 2384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The executeOrder function is external with no validation performed on the tickBeforeSwap and tickAfterSwap values to ensure that they align with the pool state.
As a result a malicious actor can trigger limit orders when they are not actually ﬁlled causing accounting issues within the system and of course defeating the purpose of a limit order.

## Recommendation
Add access controls to the executeOrder function such that it is only callable by the LimitOrderHook contract.
