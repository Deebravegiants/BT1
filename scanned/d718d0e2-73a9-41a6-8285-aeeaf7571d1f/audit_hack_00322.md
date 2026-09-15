# [M] BeatSwap incident: BeatSwap (BeatXswap) on BSC was exploited after LiquidityVestingConvert used Uniswap V3 slot0() spot price as its sole oracle, wit

## Summary
Severity: Medium
Target: BeatSwap
Loss: $ 77,512
Attack method: Price Manipulation
Published: 2026-09-09
Source: https://x.com/SlowMist_Team/status/2098314846765015062
Type: slowmist-incident

## Details
BeatSwap (BeatXswap) on BSC was exploited after LiquidityVestingConvert used Uniswap V3 slot0() spot price as its sole oracle, with no TWAP or deviation checks. The attacker flash-loaned 6,000,000 BTX, dumped it to crash sqrtPriceX96, then called deposit() twice (10,000 + 2,000 USDT) to mint LP at the manipulated price and drain 2,984,557 BTX (~$77,512).
