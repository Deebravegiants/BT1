# [M] UniswapV3AssetModule exposure can be manipulated by withdrawing zero amounts

## Summary
Severity: Medium
Contest weight: 0.5314
Dataset id: 3067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Exposure limits for Uniswap V3 positions can be bypassed. The exposure limits are a defense mechanism against price manipulation attacks and so bypassing them would allow an attacker to deposit large amounts of inflated assets to then steal other assets.

The AbstractDerivedAssetModule keeps track of the exposure of each asset.
```solidity

## Recommendation
```solidity
