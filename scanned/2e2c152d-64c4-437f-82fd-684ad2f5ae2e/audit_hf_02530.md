# [H] Indexing issues in RebalancingLib lead to undefined rebalancing behavior

## Summary
Severity: High
Contest weight: 0.1628
Dataset id: 13530
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RebalancingLib contains the previewRebalancingOrders() and previewReserveRebalancingOrders() functions. These functions generate the orders for the rebalancing and reserve rebalancing respectively. It is critical that both the rebalancing and reserve rebalancing algorithms use the correct indexes. Failing to do so doesn't result in an immediate loss of funds, but the protocol ends up in an undefined state. For example, orders can be sent to the wrong chains and the rebalancing can get stuck. In the best case, only significant action by the governance could save the protocol.

## Recommendation
Wrong indexes are used in multiple instances. The diff contains the fixes along with the reasoning for each instance.
