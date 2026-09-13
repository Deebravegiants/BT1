# [M] Fractal Protocol incident: Fractal Protocol’s USDF vault on Arbitrum was exploited via a smart contract logic flaw. The attacker used an Aave V3 USDC.e flash

## Summary
Severity: Medium
Target: Fractal Protocol
Loss: $ 13,700
Attack method: Smart Contract Vulnerability
Published: 2026-05-22
Source: https://x.com/DefimonAlerts/status/2058619391776878967
Type: slowmist-incident

## Details
Fractal Protocol’s USDF vault on Arbitrum was exploited via a smart contract logic flaw. The attacker used an Aave V3 USDC.e flash loan, looped through Balancer V2 batchSwap callbacks, and recursively called the vault’s deposit (0xb6b55f25) and withdraw functions. This exploited the fixed daily-accrued tokenPrice (~1.27 USDC/USDF) and share-rounding accounting issues without proper invariant checks across re-entrant flows, allowing the extraction of approximately 13,700 USDC.e. The vault’s liquid USDC buffer dropped from around 14,778 USDC to near zero. Pre-hack TVL was approximately 97,270 USD.
