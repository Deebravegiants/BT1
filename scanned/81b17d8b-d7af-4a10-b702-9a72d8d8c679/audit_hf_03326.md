# [M] ORDH-3 | Short Term Risk Free Trade With Limit Orders

## Summary
Severity: Medium
Contest weight: 0.0941
Dataset id: 18177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious trader may be able to execute a profitable short-term risk-free trade by creating a limit order, observing the price it will be executed at and optionally front-running the execution to update or cancel the order. This way the order is cancelled/frozen if price doesn’t move in a direction that benefits the trader in the blocks between where the execution price is from and the current execution block.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/ORDH-3.ts

## Recommendation
Ensure order fees are sufficient to invalidate short term risk-free trades. Otherwise, do not allow users to decide whether or not their order is executed by cancelling or updating the order right before execution.
