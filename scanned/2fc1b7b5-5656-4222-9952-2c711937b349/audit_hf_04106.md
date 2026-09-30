# [M] ORDM-20 | orderToPositionId Not Cleared On Settlement

## Summary
Severity: Medium
Contest weight: 0.0459
Dataset id: 20563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After an order is settled, it still exists in the orderToPositionId mapping although it has been deleted from the pendingOrders mapping. This contrasts with the functionality in function cancelPendingOrder() where the order is deleted from both mappings.

## Recommendation
Perform delete orderToPositionId[_orderId]; at the end of settlement.
