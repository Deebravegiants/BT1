# [M] Balancer V1 incident: An attacker exploited a rounding/precision vulnerability in legacy Balancer V1 contracts. Using flash loans to compress WBTC reser

## Summary
Severity: Medium
Target: Balancer V1
Loss: $ 234,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-31
Source: https://x.com/SlowMist_Team/status/2094272540193722744
Type: slowmist-incident

## Details
An attacker exploited a rounding/precision vulnerability in legacy Balancer V1 contracts. Using flash loans to compress WBTC reserves to near-zero, they minted a large amount of BPT with only 1 satoshi of WBTC and then proportionally exited to drain DPI, USDC, WETH and WBTC from the pool.
