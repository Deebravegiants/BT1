# [M] Uniswap asset managers are missing slippage checks

## Summary
Severity: Medium
Contest weight: 0.0651
Dataset id: 15208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All Uniswap interactions are missing a deadline argument and are not setting the following slippage protection arguments in UniswapLiquidityAssetManager:
- amount0Min and amount1Min in MintParams.
- amount0Min and amount1Min in DecreaseLiquidityParams.
UniswapSwapAssetManager sets the minAmountOut value, but is not signed by the user in the circuit, so it could be gamed.

## Recommendation
These arguments should be part of the proof and the user should sign them to prevent slippage.
