# [H] H-01 | Ownership Cannot Be Synced To Base Chain

## Summary
Severity: High
Contest weight: 0.1428
Dataset id: 2006
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _updateOwnership function the executeCallback function is always invoked on the _shadow address, even when the collection is native to the current chain. In the case that the collection is native to the current chain the _shadow contract address is the address of the actual NFT collection, which does not implement the executeCallback function. As a result receptions of lzRead requests on the base collection chain will always revert, thus preventing the syncing of ownership to the base chain.

## Recommendation
Only perform the executeCallback invocation on the _shadow address if isNative is false.
