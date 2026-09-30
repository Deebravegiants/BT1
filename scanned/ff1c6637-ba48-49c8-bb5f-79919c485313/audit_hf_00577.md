# [M] M-01 | No Way Of Canceling Stuck Order

## Summary
Severity: Medium
Contest weight: 0.0724
Dataset id: 2039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For a variety of reasons keepers may not execute an order in a timely manner or at times may never execute an order. This includes not canceling an order. When this happens Umami has no functionality to cancel such an order themselves which means that the order along with any collateral provided will be stuck. This also impacts the rebalance period as there is intended to be no pending orders when the rebalance period is closed.

## Recommendation
Implement functionality for the keeper to call GMX's cancelOrder function.
