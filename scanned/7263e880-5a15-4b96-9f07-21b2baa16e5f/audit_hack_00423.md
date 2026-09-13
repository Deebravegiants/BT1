# [M] DTXT/USDT liquidity pair on BSC incident: The DTXT/USDT liquidity pair on BSC was exploited. The attacker exploited a forgeable liquidity-addition detection logic in the DT

## Summary
Severity: Medium
Target: DTXT/USDT liquidity pair on BSC
Loss: $ 35,041
Attack method: Business Logic Vulnerability
Published: 2026-06-05
Source: https://x.com/SlowMist_Team/status/2062876917045608594
Type: slowmist-incident

## Details
The DTXT/USDT liquidity pair on BSC was exploited. The attacker exploited a forgeable liquidity-addition detection logic in the DTXT contract (by sending a small amount of USDT directly to the pair address, tricking the contract into classifying large sells as liquidity additions). This bypassed sell fees and drained the pool, resulting in a loss of approximately $35,041 USDT.
