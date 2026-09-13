# [M] Drips Network incident: DeFi streaming payments protocol Drips Network was exploited on July 14, 2026. The attacker used an unsafe integer cast vulnerabil

## Summary
Severity: Medium
Target: Drips Network
Loss: $ 24,900
Attack method: Smart Contract Vulnerability
Published: 2026-07-14
Source: https://olympixai.medium.com/summer-fi-lumi-finance-drips-network-6-3m-lost-to-assumptions-nobody-tested-57f1769bda14
Type: slowmist-incident

## Details
DeFi streaming payments protocol Drips Network was exploited on July 14, 2026. The attacker used an unsafe integer cast vulnerability (uint128 to int128) in the DaiDripsHub.give() function on Ethereum, causing a negative value to flip positive and reverse the transfer direction, draining 24,882.99 DAI (~$24,900) from the DaiReserve.
