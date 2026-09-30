# [M] M-02 | Permissionless Use Of Pools

## Summary
Severity: Medium
Contest weight: 0.1127
Dataset id: 2397
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Gamma allows for orders to be created/cancelled/executed for arbitrary pools. This may allow a malicious token pair to take advantage of user's locked up funds after creating orders, to prevent token transfer when claiming/cancelling and lead to loss of user funds. A malicious token can be used to create a pool which orders are created for on Gamma. The malicious token could intentionally allow an execution to occur of limit orders, with an overflow of orders being assigned as keeper executable. Before the keeper’s execution of the orders the malicious token could be updated to expend a significant amount of gas and even store this gas in a canonical “gas token” to extract value from the keeper.

## Recommendation
Consider whitelisting the pools that are allowed to be used with the Gamma limit system to avoid the risk of malicious tokens in arbitrary pools.
