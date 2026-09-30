# [M] Inability to Close Positions with Significant Positive PnL

## Summary
Severity: Medium
Contest weight: 0.0595
Dataset id: 11132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Presently, when there isn't adequate liquidity in the OstiumVault to cover profits for trades with substantial positive PnL, a revert occurs. While this behavior is intended, it's worth considering implementing a solution to partially receive the profit up to a maximum threshold or at least the collateral itself. Otherwise, traders won't be able to exit a position at all.

## Recommendation
Recommendation not found
