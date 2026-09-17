# [M] Ink Finance incident: Ink Finance’s Workspace Treasury Proxy contract on Polygon was exploited due to a whitelist validation logic flaw. The attacker de

## Summary
Severity: Medium
Target: Ink Finance
Loss: $ 140,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-11
Source: https://www.cryptotimes.io/2026/05/11/ink-finance-exploited-on-polygon-140k-usdt-drained-in-flash-loan-attack/
Type: slowmist-incident

## Details
Ink Finance’s Workspace Treasury Proxy contract on Polygon was exploited due to a whitelist validation logic flaw. The attacker deployed a malicious contract matching a whitelisted claimer address, passed authentication checks via the claim() function, and drained approximately $140,000 USDT (amplified with a ~$25K Balancer V2 flash loan).
