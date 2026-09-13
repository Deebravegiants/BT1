# [H] ZKSwap incident: ZKSwap’s Ethereum Layer 1 bridge suffered an exploit in which the attacker leveraged its emergency withdrawal mechanism, resulting

## Summary
Severity: High
Target: ZKSwap
Loss: $ 5,000,000
Attack method: Contract Vulnerability
Published: 2025-07-09
Source: https://blockaid.io/blog/how-zkswaps-5m-exploit-couldve-been-prevented-with-onchain-monitoring
Type: slowmist-incident

## Details
ZKSwap’s Ethereum Layer 1 bridge suffered an exploit in which the attacker leveraged its emergency withdrawal mechanism, resulting in a loss of approximately $5 million. Analysis revealed that the component responsible for verifying zero-knowledge proofs had failed to actually perform the verification. This critical oversight allowed the attacker to forge arbitrary withdrawal proofs, effectively bypassing the bridge’s core security guarantees.
