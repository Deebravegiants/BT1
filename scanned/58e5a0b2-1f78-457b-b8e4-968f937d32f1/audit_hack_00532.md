# [C] SwapNet incident: SwapNet’s closed-source aggregator contracts were exploited via an arbitrary-call vulnerability due to insufficient input validati

## Summary
Severity: Critical
Target: SwapNet
Loss: $ 13,430,000
Attack method: Smart Contract Vulnerability
Published: 2026-01-25
Source: https://x.com/PeckShieldAlert/status/2015608261119217671
Type: slowmist-incident

## Details
SwapNet’s closed-source aggregator contracts were exploited via an arbitrary-call vulnerability due to insufficient input validation on user-controlled parameters. This allowed attackers to abuse existing token approvals (especially from users who disabled Matcha Meta’s One-Time Approval) to execute unauthorized transferFrom calls, draining ~$13.43M across Base, Ethereum, Arbitrum, and BSC. The attacker swapped large amounts of USDC to ETH on Base and bridged funds. Matcha Meta and 0x core contracts were unaffected.
