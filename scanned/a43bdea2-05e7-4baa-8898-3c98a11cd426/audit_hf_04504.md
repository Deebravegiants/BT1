# [M] M-11 | Uniswap Rounding Can Create Insolvent Positions

## Summary
Severity: Medium
Contest weight: 0.1007
Dataset id: 22067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Uniswap V3 the getAmount0Delta function rounds in the favor of the Uniswap protocol and against the user. Specifically, when supplying liquidity the amount in is rounded up and when burning liquidity the amountOut is rounded down. This behavior results in potentially insolvent positions as the collateralization requirement may not have the same rounding against the user. For example, only one amount can be rounded by 1 wei since the position is assumed to be entirely in one asset. Additionally, the position may not be subject to precision loss at the max tick, but could be at the current tick.

## Recommendation
Consider requiring an additional minimal amount of collateral to address any potential rounding from Uniswap that may occur. This amount could be as small as 2 wei.
