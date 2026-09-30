# [M] QUEUE-1 | Missing queuedTimestamp Update

## Summary
Severity: Medium
Contest weight: 0.0508
Dataset id: 101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reduceQueuedDeposit function neglects to update the queuedTimestamp of the queuedDeposit, however in the reduceQueuedWithdrawal function the queuedTimestamp is updated. Any systems relying on this information would be misinformed as the queuedTimestamp is not correctly updated.

## Recommendation
Update the queuedTimestamp in the reduceQueuedDeposit function for consistency.
