# [M] donateETH funds are stuck in OptimismPortal

## Summary
Severity: Medium
Contest weight: 0.0522
Dataset id: 14012
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Blast OptimismPortal inherits the donateETH function from Optimism. It's not needed in Blast as it was used for the migration to bedrock. The donated funds will be stuck in the contract. When withdrawing, the withdrawal transaction's ETH is claimed from the yield manager.

## Recommendation
Consider removing this function if it is not expected to be needed or forward the donated funds to the yield manager.
