# [M] Molt EVM incident: Molt EVM, an experimental self-replicating ERC-20 token protocol on Base, was exploited due to a weak access control flaw. The att

## Summary
Severity: Medium
Target: Molt EVM
Loss: $ 127,000
Attack method: Smart Contract Vulnerability
Published: 2026-03-07
Source: https://x.com/MeiMighty1/status/2031160110714679490
Type: slowmist-incident

## Details
Molt EVM, an experimental self-replicating ERC-20 token protocol on Base, was exploited due to a weak access control flaw. The attacker deployed a malicious contract to bypass the onlySpawnerToken modifier, minted large amounts of tokens via mintFromSpawner(), and dumped them through liquidity pools for profit.
