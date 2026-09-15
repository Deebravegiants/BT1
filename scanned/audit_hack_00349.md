# [H] KiiChain incident: An attacker exploited vulnerabilities in the shared Cosmos EVM module (an arithmetic underflow in the staking precompile’s balance

## Summary
Severity: High
Target: KiiChain
Loss: $ 9,700,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-22
Source: https://x.com/KiiChainio/article/2091721027583709214
Type: slowmist-incident

## Details
An attacker exploited vulnerabilities in the shared Cosmos EVM module (an arithmetic underflow in the staking precompile’s balance write-back after delegation, combined with vesting account handling and other undisclosed bugs). By creating a vesting account and deploying a contract to it, the attacker repeated the technique 18 times, draining approximately 148.3 million KII from various wallets. KiiChain halted the network at block 9355723 to stop further theft.
