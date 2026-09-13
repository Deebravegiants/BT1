# [M] Unnamed BSC DEX Router incident: An unnamed DEX router on BNB Chain was exploited because uniswapV3SwapCallback did not authenticate a real V3 pool. The attacker u

## Summary
Severity: Medium
Target: Unnamed BSC DEX Router
Loss: $ 46,070
Attack method: Smart Contract Vulnerability
Published: 2026-09-07
Source: https://x.com/SlowMist_Team/status/2097153762746159228
Type: slowmist-incident

## Details
An unnamed DEX router on BNB Chain was exploited because uniswapV3SwapCallback did not authenticate a real V3 pool. The attacker used a fake pool, set victims as payer, and drained existing token allowances via transferFrom, stealing about 62.28 WBNB from 29 wallets in one transaction.
