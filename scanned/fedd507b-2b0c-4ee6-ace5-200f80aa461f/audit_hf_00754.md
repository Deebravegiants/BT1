# [H] H-04 | Unrestricted burn Could Lead To Unsettled Bonds

## Summary
Severity: High
Contest weight: 0.1479
Dataset id: 2314
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
burn can be called by anyone at any market state, allowing users to burn their yes and no tokens to
retrieve the deposit tokens.
This could cause issues in a scenario where the market is finalized, especially when the winning
position is _CANCELED. Instead of calling withdrawFromCanceledMarket, users might choose to call
burn to reclaim their deposit tokens.
This would prevent _settleBonds from being triggered, causing all bonds and rewards to remain
stuck and unresolved.

## Recommendation
Consider restricting burn so it can only be called when the market is not finalized. Additionally, make
settle bonds publicly callable in cases where no token holders decide to redeem or withdraw their
tokens.
