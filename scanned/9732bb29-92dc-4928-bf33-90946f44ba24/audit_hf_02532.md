# [H] Indexing issues in ConfigBuilder lead to corrupted anatomy data when rebalancing is finished

## Summary
Severity: High
Contest weight: 0.1493
Dataset id: 13532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The wrong indexing is used in ConfigBuilder.startRebalancing() and ConfigBuilder.finishRebalancing(). In the ConfigBuilder.startRebalancing() function the wrong indexing simply causes the function to revert in some cases since chainOrders[chainIndex] accesses chainOrders with an out-of-bounds index. On the other hand, in the ConfigBuilder.finishRebalancing() function, wrong results can be assigned to the data structures that keep track of the new anatomy. This not only makes rebalancing get stuck, it also corrupts the protocol's data.

## Recommendation
The diff contains the fixes along with the reasoning for each instance.
