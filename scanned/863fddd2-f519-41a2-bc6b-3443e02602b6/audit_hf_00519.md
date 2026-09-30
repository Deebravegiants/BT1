# [M] M-10 | resolutionCallback Fails On Small Amounts

## Summary
Severity: Medium
Contest weight: 0.1063
Dataset id: 1977
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function _createEpochAndPosition passing is critical to the Vault's flow, since if the resolutionCallback fails the Vault's functionality is stopped. If the Vault has more collateral than the current minimum collateral, the Vault attempts to _createNewLiquidityPosition. The issue is that even with enough collateral to meet the minimum threshold, is it not guaranteed that the liquidity to-be minted from the calculated amount0 and amount1 is greater than 0 due to Uniswap rounding down on small amounts, which would trigger a revert in UniswapV3Pool.mint: require(amount > 0); Ultimately, the Vault will attempt to mint which will revert, causing the callback to fail and the mints/epoch creation will not occur.

## Recommendation
Consider enforcing a higher minimum collateral.
