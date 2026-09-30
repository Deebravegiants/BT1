# [C] reduceOnly limit order update does not take into account that a new amm may be selected, which may lead to loss of funds

## Summary
Severity: Critical
Contest weight: 0.1671
Dataset id: 10781
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
On a limit order update, in _updateLimitOrder(), changing amm is not being taken into account. The following scenarios are possible:
- if reduceOnly remains false, no problem
- if reduceOnly goes from false to true, no problem
- if reduceOnly remains true, it won't link the reduceOnly order in the new amm B, nor remove it from amm A
- if reduceOnly goes from true to false, it will remove the linked order from the new amm B, instead of the old amm A. This seems the worst scenario, as updating the limit order from false to true will pull weth from the trader, but this order may be deleted if the trader closes its position on amm A, losing the funds.

## Recommendation
Correctly handle the case when the amm changes.
