# [M] UniswapV3AssetModule calculates underlying asset amounts irrespective of amount parameter

## Summary
Severity: Medium
Contest weight: 0.5339
Dataset id: 3069
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Exposure of creditors in UniswapV3AssetModule can be manipulated to the upside. This results in a DoS attack where further deposits are blocked by maxing out the exposure of a Creditor.

The UniswapV3AssetModule._getUnderlyingAssetsAmounts() function calculates the amounts of underlying tokens for a Uniswap V3 position.
```solidity

## Recommendation
Return zero amounts if amount=0. Note that the rateUnderlyingAssetsToUsd array can remain empty. In this case, the rates will be queried downstream if needed.
```solidity
