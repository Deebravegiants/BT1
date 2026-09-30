# [M] M-17 | Gas Griefing With Settlement Hooks

## Summary
Severity: Medium
Contest weight: 0.0720
Dataset id: 21117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can opt to use settle order hooks, called at the end of the settleOrder function. These hooks will be mainly used for splitting and merging accounts when settling orders. These hooks require explicit permissions from the account holders: _PERPS_MODIFY_COLLATERAL_PERMISSION. If a user commits an order with one of this hooks, they can front run the keeper order and remove the account permissions, reverting the transaction.

## Recommendation
Be aware and clearly document that this can be an issue for the keepers.
