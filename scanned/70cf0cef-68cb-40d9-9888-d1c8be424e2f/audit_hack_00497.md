# [M] LML/USDT staking protocol incident: LML/USDT staking protocol on BNB Chain suffered a price manipulation attack. The hacker used flash loans to massively inflate the

## Summary
Severity: Medium
Target: LML/USDT staking protocol
Loss: $ 950,000
Attack method: Price Manipulation
Published: 2026-03-31
Source: https://x.com/Phalcon_xyz/status/2039211832947408928
Type: slowmist-incident

## Details
LML/USDT staking protocol on BNB Chain suffered a price manipulation attack. The hacker used flash loans to massively inflate the LML/USDT pool spot price, exploited a logic flaw in the staking contract’s reward calculation (which relied on a stale stored price with a 3600-second cooldown instead of live AMM price), batch-claimed oversized LML rewards from pre-staked addresses via EIP-7702, and sold them in the distorted pool for approximately $950,000 profit, causing the LML token price to crash 99.6%.
