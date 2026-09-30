# [M] M-17 | Brokers Can Be Gas Griefed

## Summary
Severity: Medium
Contest weight: 0.1130
Dataset id: 2117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users place orders in the order book and pay a gas fee to compensate the broker that fulfils their orders. Users can also cancel their orders after a given time passes. When they do that, they will be refunded the whole gas amount they paid to compensate the broker. This can be used to place multiple always reverting orders. For example, withdrawal orders with slippage over 100%, liquidity orders that exceed the liquidity cap, or just normal orders that happen to revert. The broker will try executing them, which means it will pay gas for execution for the reverting transaction. The user can then cancel all their orders and get their funds back, resulting in lost funds for the broker.

## Recommendation
Consider splitting the paid gas in two parts - send the first part back to the user and the second part to the broker to compensate them for any order they have tried fulfilling.
