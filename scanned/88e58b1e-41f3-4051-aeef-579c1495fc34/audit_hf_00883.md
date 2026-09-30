# [M] Non EIP712 compliance in Liquidation

## Summary
Severity: Medium
Contest weight: 0.0703
Dataset id: 2639
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LiquidationManager::batchLiquidateDensWithPermit() is not EIP712 compliant as it does not hash the _denArray to include in the structHash, as per the EIP: The dynamic values bytes and string are encoded as a keccak256 hash of their contents. In LiquidationManager:599, _denArray is not hashed. Internal Pre-conditions None. External Pre-conditions None. Attack Path 1. Call LiquidationManager::batchLiquidateDensWithPermit(). Non EIP712 compliance.

## Recommendation
Hash the _denArray.
