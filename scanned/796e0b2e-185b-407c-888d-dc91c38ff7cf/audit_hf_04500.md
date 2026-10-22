# [H] H-03 | LP Stuck Because Of Underflow

## Summary
Severity: High
Contest weight: 0.2081
Dataset id: 22063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
How much amount0 and amount1 an LP provides initially and how much it receives while closing the position are subject to change based upon the pool price. Considering LP's can provide liquidity amounts larger than their collateral to the pool, the following scenario is applicable in many situations: LP's token 1 swapped to token 0 such that LP's borrowedVEth - collectedVEth amount will be bigger than LP's collateral which will result with underflow while closing the position. This occurs when attempting to deduct the collateral in _closeLiquidityPosition: position.depositedCollateralAmount = position.borrowedVEth - collectedAmount1; In this case the LP is prevented from closing their position.

## Recommendation
Allow excess debt that can’t be covered to live on in the position.borrowedVEth. Note that the case where position.borrowedVEth is left can only occur when the price of the pool has moved downwards through the LP relative to where the LP was first created. Thus the LP will take on a long position after closing and it is expected and correctly handled when a nonzero position.borrowedVEth exists.
