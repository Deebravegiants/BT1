# [H] H-01 | Pools With Low SqrtPrices Are Unusable

## Summary
Severity: High
Contest weight: 0.1907
Dataset id: 2409
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because of precision loss that occurs when converting the user’s specified amount to the order’s associated liquidity, pools for quote assets with small prices relative to the base token are unusable. This is because the creation of an order does not clear any remaining amount delta from the Uniswap PoolManager. As a result non zero balance deltas are left in the delta for the user’s input currency and therefore the NonzeroDeltaCount is not decremented to zero upon the modifyLiquidity call. This applies to tokens with a sqrtPrice in the range of 1e27 ($0.0001) and below, but also for token pairs where one token has larger decimals than the other, simulating a very low price.

## Recommendation
At the end of the CREATE_ORDERS callback, be sure to settle any dust that was left for the user by either minting it or clearing it from the PoolManager contract. Be aware that if it is cleared then this amount is lost.
