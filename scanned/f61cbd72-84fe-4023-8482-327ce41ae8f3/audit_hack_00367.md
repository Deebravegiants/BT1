# [M] Set Protocol incident: The DeFi protocol Set Protocol (involving Index Coop’s ExchangeIssuance contract) was exploited due to insufficient state locking

## Summary
Severity: Medium
Target: Set Protocol
Loss: $ 9,600
Attack method: Smart Contract Vulnerability
Published: 2026-07-30
Source: https://x.com/SlowMist_Team/status/2082767887245410320
Type: slowmist-incident

## Details
The DeFi protocol Set Protocol (involving Index Coop’s ExchangeIssuance contract) was exploited due to insufficient state locking in the smart contract. The attacker used a malicious manager pre-issue hook to artificially inflate asset valuations (e.g., positionMultiplier), causing the contract to transfer excess assets based on falsified data, resulting in a loss of approximately $9,600.
