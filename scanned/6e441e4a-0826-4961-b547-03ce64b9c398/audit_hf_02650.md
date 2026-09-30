# [M] NDC Index Shuffling Issue In LRTDepositPool

## Summary
Severity: Medium
Contest weight: 0.1181
Dataset id: 14365
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeNodeDelegatorContractFromQueue() function in LRTDepositPool contract employs a mechanism to remove a Node Delegator Contract (NDC) by swapping the target NDC with the last in the list on line [336], potentially altering NDC indices. This approach can lead to two primary issues:
1. Race Condition
Operations like transferAssetToNodeDelegator() or transferETHToNodeDelegator() may revert if they target the last NDC index which gets removed or swapped during execution.
2. Incorrect NDC Operation
If an NDC other than the last one is removed, subsequent operations might act on an incorrect NDC due to the shift in indices.

## Recommendation
Consider implementing a more stable indexing mechanism that does not rely on the position within an array or explore the possibility of using a mapping structure to track NDCs, which inherently avoids the problem of shifting indices. Additionally, introducing checks or mechanisms to handle ongoing operations gracefully during the removal process could prevent potential race conditions and ensure operational accuracy.
