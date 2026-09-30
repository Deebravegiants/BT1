# [M] M-01 | No way for user to add cancellation receiver

## Summary
Severity: Medium
Contest weight: 0.0575
Dataset id: 21454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an order gets cancelled there is a check to see if the order has a cancellationReceiver. If it does the funds will be sent there, if not then the account will get the funds. This works well, however there is no way for a user to add a cancellationReceiver when creating an order. Preventing the use of this feature.

## Recommendation
Set the cancellationReceiver when creating an order and validate that the address used is valid.
