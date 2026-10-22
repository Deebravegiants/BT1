# [H] H-1 The startSqrtPriceX96 manipulation

## Summary
Severity: High
Contest weight: 0.0932
Dataset id: 7527
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The starting price Battle.sol#L102 is an arbitrary, user-defined value. For the given battle key, an attacker can specify their unfair price to grief other users or even to make profits from unfair trade conditions. Such attacks can't be avoided without redeploying the system's smart-contract.

## Recommendation
We recommend including startSqrtPriceX96 into the battle identifier (battle key).
