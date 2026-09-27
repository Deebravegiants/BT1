# [M] Mure incident: Mure’s MureDistribution proxy contract on Ethereum was exploited due to an access control vulnerability in signature validation. T

## Summary
Severity: Medium
Target: Mure
Loss: $ 11,700
Attack method: Smart Contract Vulnerability
Published: 2026-05-23
Source: https://x.com/clarahacks/status/2058341669603307880
Type: slowmist-incident

## Details
Mure’s MureDistribution proxy contract on Ethereum was exploited due to an access control vulnerability in signature validation. The attacker supplied a malicious contract as the “signer source,” causing SignatureChecker to return true and bypass verification. This allowed draining 4.85M QUEST tokens (pre-approved to the proxy) via transferFrom, which were then swapped for ~5.45 ETH (~$11,700) on Uniswap. No user funds or main payment infrastructure were affected; it was a targeted logic flaw in one distribution contract.
