# [M] ApeBond incident: ApeBond's ApeYieldVault smart contract on BSC was exploited. The attacker used a public helper contract to call migrateToVotingEsc

## Summary
Severity: Medium
Target: ApeBond
Loss: $ 3,421
Attack method: Smart Contract Vulnerability
Published: 2026-06-03
Source: https://x.com/clarahacks/status/2062564868130029636
Type: slowmist-incident

## Details
ApeBond's ApeYieldVault smart contract on BSC was exploited. The attacker used a public helper contract to call migrateToVotingEscrow with duplicate pool IDs, inflating a lock amount from ~1.71 quadrillion ABOND to ~29 quadrillion ABOND. They then unlocked, claimed the inflated lock, sold ABOND in the public ABOND/WBNB pool, repaid a Moolah flashloan, and kept ~5.72 WBNB profit. The entire flow was permissionless and on-chain.
