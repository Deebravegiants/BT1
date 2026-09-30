# [C] C-01 | Liquidations Prevented With updateOrder

## Summary
Severity: Critical
Contest weight: 0.1765
Dataset id: 21451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
createOrder checks every new decrease order for if it will pass over the max autoCancel gas limit using validateTotalCallbackGasLimitForAutoCancelOrders. However the same check is missed inside updateOrder, enabling the user to:
1. Create 5 decrease orders with their max allowed callback gas, without putting them inside the autoCancel list.
2. Call updateOrder for all of these order with autoCancel variable set to true. With this method users can bypass 5 million maximum callback gas limit for Auto Cancel orders and reach up to 10 million. Which will result in reverting liquidations because gas required to liquidate will bypass block gas limit in avalanche.

## Recommendation
Add the validateTotalCallbackGasLimitForAutoCancelOrders validation inside updateOrder.
