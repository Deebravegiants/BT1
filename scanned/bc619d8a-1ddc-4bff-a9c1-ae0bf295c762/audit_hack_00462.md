# [H] Aftermath Finance incident: Aftermath Finance, a decentralized perpetuals trading platform built on the Sui blockchain, suffered a security exploit in its per

## Summary
Severity: High
Target: Aftermath Finance
Loss: $ 1,140,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-29
Source: https://x.com/AftermathFi/status/2049681357559808130
Type: slowmist-incident

## Details
Aftermath Finance, a decentralized perpetuals trading platform built on the Sui blockchain, suffered a security exploit in its perpetuals (perps) protocol. The vulnerability stemmed from a flaw in the fee accounting logic, specifically allowing negative "builder code" fees to be set. This enabled the attacker to inflate synthetic collateral and drain funds from the protocol's vault.The attacker drained approximately $1.14 million in USDC across 11 transactions within about 36 minutes. Blockchain security firm Blockaid detected and flagged the attack in real time (attacker address starting with 0x1a65...2d41e). Aftermath Finance promptly paused the affected perpetuals product and collaborated with security partners including Blockaid and CertiK for investigation. The team confirmed that the exploit was isolated to the perpetual futures market; spot trading, AMM pools, afSUI staking, and other products remained unaffected.
