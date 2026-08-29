# [H] Non-negligible precision loss for tokens that have small decimals

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/56
Type: sherlock-finding

## Details
Koolex

high

# Non-negligible precision loss for tokens that have small decimals

## Summary
Non-negligible precision loss in `ratePerSecond()` function for tokens that have less than 6 decimals such as GUSD (Gemini dollar). 

## Vulnerability Detail
Let's assume:
1. Stream amount = 1M, 
2. Duration = 31_557_600 seconds (1 year)

We would have
- ratePerSecondWithoutLoss = 1000000 / 31_557_600 = 0.031688087814029
- Max round down impact = duration - 1 = 31_557_599


Let's apply the math on 3 tokens USDC, GUSD and WETH

- **USDC (6 decimals):**
            `ratePerSecond()` = 0.031688 
            lossPerSecond = ratePerSecondWithoutLoss - ratePerSecond
            lossPerSecond = 0.000000087814029
            lossPer(Year-1) = 31_557_599 * lossPerSecond = 2.771199912185947 USDC which is negligible

- **GUSD (2 decimals):**
            `ratePerSecond()` = 0.03 since 
            lossPerSecond = ratePerSecondWithoutLoss - ratePerSecond
            lossPerSecond = 0.001688087814029
            lossPer(Year-1) = 31_557_599 * lossPerSecond = 53271.998311913756371 GUSD which is not negligible
  
- **WETH (18 decimals):**
            `ratePerSecond()` =  0.031688087814028950 
            lossPerSecond = ratePerSecondWithoutLoss - ratePerSecond
            lossPerSecond = 0,000000000000000050
            lossPer(Year-1) = 31_557_599 * lossPerSecond = 0.00000000157788 WETH which is negligible

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/56_
