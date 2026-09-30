# [H] H-04 | Risk-Free Trades With payDebt

## Summary
Severity: High
Contest weight: 0.2817
Dataset id: 22081
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. When a trader's collateral and positions are slightly above the threshold to allow creating the wished order, the order can be created, but trying to settle it a few blocks later will revert because interest is accrued every second.
2. Users are not allowed to deposit funds while they have a pending order waiting to be settled, because of the checkPendingOrder check. This can be bypassed by calling the payDebt function instead.
3. Orders can be executed after commit time + delay and till the expiry of the order. The price at commit time + delay is used even if the order is executed later than that (somewhere between this timestamp and the expiry timestamp)
A malicious actor can abuse these conditions to create a risk-free trade:
• The attacker owns an account that has a big amount of collateral, some debt, and a small position that accrues interest every second
• Attacker creates an order that requires exactly the available margin to be created
• A small amount of interest accumulates till the order can be settled
• Keepers are not able to settle the order because the attacker does not have enough available margin now
• The attacker waits if the price changes so that the order would be instant profit and if so increases the available margin by calling payDebt

## Recommendation
Add the AsyncOrder.checkPendingOrder(account.id); check to the payDebt function.
