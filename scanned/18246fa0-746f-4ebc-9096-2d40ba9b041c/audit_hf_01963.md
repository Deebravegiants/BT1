# [C] CRT-1 Infinity minting issue

## Summary
Severity: Critical
Contest weight: 0.1685
Dataset id: 11043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue is about the ERC721OTransferable contract's function _batchTransferFrom introducing the way to wreck the user's balances allowing for the position holder to transfer a batch of the positions to itself in here: ERC721OTransferable.sol on lines 122,123,124,125,126,127,128.
This can lead to the balances increase/decrease, unexpected by the applcation's logic, which can only be fixed with contract redeployment and manual data recovery.
Even being called from safeBatchTransferFrom in here: ERC721OTransferable.sol#L30 (the function's name is misleading, by the way) it still can lead to the wreckage.

## Recommendation
It is recommended to introduce additional requirement for the function's arguments from and to not to be equal.
2.2 MAJOR
