# [M] CometDEX incident: The BLND-USDC liquidity pool of CometDEX (Comet AMM) on the Stellar network was exploited due to an accounting bug that allowed sa

## Summary
Severity: Medium
Target: CometDEX
Loss: $ 717,518.92
Attack method: Smart Contract Vulnerability
Published: 2026-08-25
Source: https://x.com/blend_capital/status/2092288347766984713
Type: slowmist-incident

## Details
The BLND-USDC liquidity pool of CometDEX (Comet AMM) on the Stellar network was exploited due to an accounting bug that allowed same-asset swaps (USDC→USDC), corrupting reserve calculations. The attacker used flash loans from a Blend pool and repeated the process about 36 times to extract excess funds, resulting in a loss of approximately $717,518.92 USDC. Funds were subsequently moved.
