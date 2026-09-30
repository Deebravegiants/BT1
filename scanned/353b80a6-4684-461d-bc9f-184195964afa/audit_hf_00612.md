# [M] M-11 | Broker Should Be Paid For Cancelling Orders

## Summary
Severity: Medium
Contest weight: 0.0893
Dataset id: 2111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Brokers have the ability to cancel stale position and withdrawal orders and the gas fees incurred for these cancellations are refunded to the user who created the order. This design leaves brokers unreimbursed for the gas costs of performing the cancellations. A malicious actor can exploit this by creating multiple orders with unrealistic limit prices, ensuring that the orders never get filled and eventually go stale. The broker would then be forced to expend gas to cancel these orders repeatedly, incurring significant costs without compensation.

## Recommendation
Deduct a portion of gas fees to reimburse the broker when orders are cancelled.
