# [H] Nullify Order ID status after confirmation in confirmOrderV3

## Summary
Severity: High
Contest weight: 0.1844
Dataset id: 6221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the confirmOrderV3 function, the order ID is not nullified after confirmation, which allows the same order to potentially be confirmed by two different relayers if the transactions are executed in the same block. This could lead to a scenario where only one of the two relayers that fulfilled and confirmed the order would be able to claim the payout on the source chain. A hash of amount, asset, target, and orderId can be used as a status key to ensure a unique mapping for the oder status.

## Recommendation
For the status mapping a hash of amount, asset, target, and orderId can be used.
1. Add a check at the beginning of the function to verify if the order has already been confirmed by checking the confirmation status using a hash of amount, asset, target, and orderId.
2. After successfully confirming the order, mark it as confirmed in storage by setting a true value in the confirmation status mapping (using the hash as the key). This ensures that once an order (and parameters) is confirmed, it cannot be re-confirmed by another relayer, preventing the second relayer from losing the funds.
