# [H] Raydium incident: Solana-based decentralized exchange Raydium disclosed a vulnerability in its deprecated AMM V3 program (phased out in 2021), which

## Summary
Severity: High
Target: Raydium
Loss: $ 1,340,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-10
Source: https://x.com/0xINFRA/status/2064738005697384476
Type: slowmist-incident

## Details
Solana-based decentralized exchange Raydium disclosed a vulnerability in its deprecated AMM V3 program (phased out in 2021), which allowed an attacker to drain approximately $1.34 million from five inactive liquidity pools (Sollet USDT-RAY, Sollet ETH-RAY, SRM-RAY, USDC-RAY, and RAY-SOL). The flaw was due to insufficient validation of LP mint addresses, enabling the attacker to create a fake LP token and bypass proportion checks to withdraw funds. No current users, active programs, SDK, or dApp were affected. Raydium will fully compensate losses from its treasury and is conducting a security review of mainnet programs.
