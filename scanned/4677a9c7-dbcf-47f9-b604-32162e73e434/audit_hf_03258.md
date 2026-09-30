# [M] GLOBAL-9 | Possible Loss of Funds

## Summary
Severity: Medium
Contest weight: 0.0621
Dataset id: 17880
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating a decrease order or a swap order, there is no validation that the receiver address is not the zero address. In this case, when the order is executed and a swap takes place, the user’s funds will be left in the MarketToken, otherwise if no swap is executed during the decrease, the funds would be sent to the zero address.

## Recommendation
Do not allow users to possibly lose funds this way and validate that the receiver is not the zero address for decrease and swap orders.
