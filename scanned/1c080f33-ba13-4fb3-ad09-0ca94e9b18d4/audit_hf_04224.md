# [M] M-18 | Order Cancellation Overcompensates Keepers

## Summary
Severity: Medium
Contest weight: 0.1155
Dataset id: 21118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon cancelling an order, the keeper is compensated with the same fee they would receive for executing the order. However the gas cost necessary to execute an order is far more than the gas cost to cancel an order. Additionally, keepers will receive the keeperFeeBufferUsd as profit when cancelling an order, when this amount is meant instead to incentivize the execution of an order. As a result keepers receive far more profit for cancelling orders rather than executing them. Therefore, keepers will not only be overcompensated for cancellation, but highly incentivized to front-run users who are cancelling their own orders to cancel them on the user’s behalf and collect a fee from the user’s margin.

## Recommendation
Consider implementing a fee calculation that is specific to cancellation remuneration rather than overcompensating keepers for the cancellation with the same fee they would receive from execution.
