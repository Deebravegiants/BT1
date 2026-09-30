# [M] Calling batchProcessDeposit() before batchProcessWithdrawal() allows bypassing exposure limits

## Summary
Severity: Medium
Contest weight: 0.5348
Dataset id: 3068
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Exposure limits for Uniswap V3 positions can be bypassed. The exposure limits are a defense mechanism against price manipulation attacks and so bypassing them would allow an attacker to deposit large amounts of inflated assets to then steal other assets. When a user deposits assets through UniswapV3AssetModule.processDirectDeposit(), it first makes a call to UniswapV3AssetModule._addAsset()
```solidity

## Recommendation
Perform the withdrawal before the deposit.
```solidity
