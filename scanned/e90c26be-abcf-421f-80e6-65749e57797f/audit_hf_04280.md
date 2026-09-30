# [M] M-03 | MAX_AUTO_CANCEL_ORDERS Update Risk

## Summary
Severity: Medium
Contest weight: 0.1041
Dataset id: 21419
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is completely closed (via user or by liquidation), user's orders in autoCancelList will be cancelled via providing MAX_AUTO_CANCEL_ORDERS as a max index to auto cancel list. If that variable changes to a variable that is less, then some orders will stay at the unreachable part of the autoCancel list. If user continues to use the system, these orders can be executed when they are not expecting. Since auto cancellation process is gas intensive, MAX_AUTO_CANCEL_ORDERS is a variable that can be changed more than other variables to limit the gas usage of a single call. Hence it is very possible for this problem to occur in production.

## Recommendation
In the case of the aforementioned variable is changed, inform users so that they can cancel their orders.
