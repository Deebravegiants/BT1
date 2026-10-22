# [M] ATOHook incident: ATOHook smart contract was exploited due to a storage slot collision between the rewards mapping and Solady’s fixed ReentrancyGuar

## Summary
Severity: Medium
Target: ATOHook
Loss: $ 25,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-01
Source: https://x.com/SlowMist_Team/status/2063576945552462201
Type: slowmist-incident

## Details
ATOHook smart contract was exploited due to a storage slot collision between the rewards mapping and Solady’s fixed ReentrancyGuard slot. The nonReentrant modifier in getReward() wrote a sentinel value that was misinterpreted as a reward balance for a colliding address, allowing the attacker to repeatedly claim and drain a fixed amount of ETH (200 times), stealing approximately 14.41 ETH.
