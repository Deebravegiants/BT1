# [C] GLOBAL-1 | Homogeneous Markets Double Count Value

## Summary
Severity: Critical
Contest weight: 0.2303
Dataset id: 18165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When using the getPoolValue function for markets with identical long and short backing tokens, the cache.longTokenAmount and cache.shortTokenAmount represent the same token amount. However both of these token amounts are counted in the value of the pool. Therefore the deposited pool value is doubled. Additionally, several validations e.g. validateReserve, validateMaxPnl, and validatePoolAmount among others are immediately invalidated as they errantly count the same exact token amount for both the short and long side. This way the single backing token pool is effectively double counted as backing both long positions and short positions. Similarly open interest in these markets is double counted in the getNextFundingAmountPerSize function, producing a completely invalid calculation for funding fees.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GLOBAL_1.ts

## Recommendation
Reconsider if markets with the same backing longToken and shortToken should be possible. If they should, then handle their accounting/validation separately.
