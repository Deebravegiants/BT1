# [M] Silo Labs incident: According to Silo Labs' postmortem report, an unreleased leverage feature smart contract deployed on Ethereum mainnet and Sonic wa

## Summary
Severity: Medium
Target: Silo Labs
Loss: $ 542,000
Attack method: Contract Vulnerability
Published: 2025-06-25
Source: https://silofinance.medium.com/post-mortem-unreleased-leverage-contract-exploitd-0ab8f37afcbb
Type: slowmist-incident

## Details
According to Silo Labs' postmortem report, an unreleased leverage feature smart contract deployed on Ethereum mainnet and Sonic was exploited during its testing phase. The affected contract was separate from Silo’s core infrastructure.

The attacker manipulated the _swapArgs parameter within the contract to execute unauthorized borrowing, leveraging user approvals granted during testing. The exploit resulted in a loss of 224 ETH, which belonged to SiloDAO. No user funds were at risk, as the feature had not yet been made public.
