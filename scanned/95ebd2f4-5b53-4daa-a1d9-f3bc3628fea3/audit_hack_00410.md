# [M] DIP incident: The DIP token contract (Etherisc ecosystem) was exploited due to a missing return statement in the _transfer() function for Pancak

## Summary
Severity: Medium
Target: DIP
Loss: $ 111,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-17
Source: https://x.com/SlowMist_Team/status/2067078816514908286
Type: slowmist-incident

## Details
The DIP token contract (Etherisc ecosystem) was exploited due to a missing return statement in the _transfer() function for PancakeSwap-routed trades, causing double transfers. The attacker used skim(router) and sync() to manipulate the pool and drain ~$111K USDC.
