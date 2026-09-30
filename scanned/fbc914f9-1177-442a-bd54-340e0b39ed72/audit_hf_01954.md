# [M] It's possible to mint an infinite number of shares without increasing quote or base amounts, due to rounding down

## Summary
Severity: Medium
Contest weight: 0.1042
Dataset id: 10804
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For very low notional amounts, when adding liquidity, invariantIncrease is always bigger than 0 (not true for the first depositer though), but the corresponding quote and base amounts might be 0. This means that malicious users could loop addLiquidity() calls, minting a very low amount of shares each time, without ever increasing quote and base. It is most likely not profitable to perform this shares inflation, but some way could be found to exploit it in a way that is profitable. Plugging in some numbers, it was found that it is possible to mint 22 shares with 0 quote and base amount, which if looped enough times could change the pool state significantly.

## Recommendation
Add a minimum notional amount when adding liquidity to reduce the attack surface.
