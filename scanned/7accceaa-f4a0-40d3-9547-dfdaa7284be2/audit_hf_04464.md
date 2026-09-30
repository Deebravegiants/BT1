# [M] M-06 | DoS When Orders Are Stuck In GMX

## Summary
Severity: Medium
Contest weight: 0.0487
Dataset id: 21960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX keepers will not always execute orders in a reasonable amount of time. For reasons outside of the creators control. With no functionality to manually cancel these orders an order can be sitting for a prolonged period of time halting any other order operations.

## Recommendation
Consider adding functionality for keepers to cancel orders after a certain amount of time.
