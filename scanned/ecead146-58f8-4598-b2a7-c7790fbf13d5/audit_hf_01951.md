# [M] _getPriceToTick() reverts if the price is smaller than 1e10, which may amm

## Summary
Severity: Medium
Contest weight: 0.0515
Dataset id: 10791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
means that if a significant chunk of the liquidity is in the limit orders, if a user has an order bigger than the current amm liquidity, it may return 1e7 from amm.getMarkPriceAfterOpen(), which reverts in _getPriceToTick(), as it divides by 1e10 and reverts when calculating the tick.

## Recommendation
Return 1e10 instead of 1e7 so that it does not round down to 0 in _getPriceToTick().
