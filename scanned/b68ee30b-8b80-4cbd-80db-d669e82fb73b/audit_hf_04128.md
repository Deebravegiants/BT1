# [M] ADAP-3 | Adapter And Order Manager Discrepancies

## Summary
Severity: Medium
Contest weight: 0.1087
Dataset id: 20588
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For any keepers or users viewing a position’s status through the Adapter, it is important to document some of the differences between it's behavior and the behavior in OrderManager. Some differences include but are not limited to: `_verifyAndUpdatePrice` reverts if the difference between the primary and secondary price is exceeded in the OrderManager. In the Adapter, the primary price is simply used. `getPriceWithDeviation` does not consider whether the order is an increase or decrease order for deviation and rounding because in the OrderManager it is called in the context of recreating a position regardless of the direction. In the Adapter, it can take into account order direction.

## Recommendation
Clearly document the differences between Adapter and OrderManager functionalities and their reasons.
