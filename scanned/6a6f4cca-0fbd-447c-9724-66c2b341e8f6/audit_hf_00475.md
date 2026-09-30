# [M] Create order can be DOSed as

## Summary
Severity: Medium
Contest weight: 0.2363
Dataset id: 1915
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Internal pre-conditions
External pre-conditions
Attack Path
Assume that:
• maxPendingOrders is set to 25, which is similar to the value configured in the test script
• minOrderSize is set to 10 USD, which is similar to the value configured in the test script
Bob (malicious user) can spend 250 USD to create 25 orders, which will cause the number of pending orders to reach the maxPendingOrders (25) limit. For each of the orders Bob created, he intentionally configured the order in a way that it will always never be in range. For instance, setting the takeProfit, stopPrice, and/or stopLimitPrice to uint256.max - 1. In this case, no one can fill his orders.
The protocol admin can attempt to delete Bob's order by calling adminCancelOrder function to remove Bob's order from the pendingOrderIds to reduce the size. When Bob's order is canceled, the 10 USD worth of assets will be refunded back to Bob.
The issue is that this protocol is intended to be deployed on Optimism as per the Contest’s README where the gas fee is extremely cheap. Thus, Bob can simply use the refunded 10 USD worth of assets and create a new order again.
Thus, whenever the admin cancels Bob's order, he can always re-create a new one again. As a result, whenever innocent users attempt to create an order, it will always revert with a "Max Order Count Reached" error.
ntracts/automatedTrigger/Bracket.sol#L444
File: Bracket.sol
444:
function _createOrder(
..SNIP..
462:
require(
    pendingOrderIds.length < MASTER.maxPendingOrders(),
    "Max Order Count Reached"
);
ntracts/automatedTrigger/StopLimit.sol#L300
File: StopLimit.sol
300:
function _createOrder(
..SNIP..
320:
require(
    pendingOrderIds.length < MASTER.maxPendingOrders(),
    "Max Order Count Reached"
);
Medium. DOS and broken functionality. This DOS can be repeated infinitely, and the cost of attack is low.

## Recommendation
Consider collecting fees upon creating new orders or canceling existing orders so that attackers will not be incentivized to do so, as it would be economically infeasible.
