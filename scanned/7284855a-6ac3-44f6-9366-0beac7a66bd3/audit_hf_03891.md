# [M] MarginDex::execute_limit_orderwill always re-

## Summary
Severity: Medium
Contest weight: 0.1358
Dataset id: 20179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All calls to the MarginDex's execute_limit_order will always revert due the limit order being cleared in storage ahead of a call to remove_limit_order. The execute_limit_order function includes the following logic... The limit order is being set to empty(LimitOrder) in storage. Then a call to self._remove_limit_order is called for the same _uid. remove_limit_order has the following logic... The newly-empty order is read from storage, and it's associated account is used fetch the limit_order_uids. The issue is that this account is the zero address, which is the default value after the order was cleared in the preceding function. This will cause the uids array to be empty, and the loop will revert when i == len(uids) - 1. This means that all calls to execute_limit_order will revert, and no limit orders can be executed, which is a major piece of functionality for the protocol.

## Recommendation
execute_limit_order should not clear the limit order in storage before calling remove_limit_order. This will allow the limit_order_uids to be fetched correctly.
