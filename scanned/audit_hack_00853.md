# [M] Magpie Protocol incident: The decentralized liquidity aggregation protocol Magpie Protocol was attacked due to a contract vulnerability, resulting in $129,0

## Summary
Severity: Medium
Target: Magpie Protocol
Loss: $ 129,000
Attack method: Contract Vulnerability
Published: 2024-04-23
Source: https://medium.com/@Magpieprotocol/magpie-protocol-smart-contract-vulnerability-post-mortem-f6400db0a25e
Type: slowmist-incident

## Details
The decentralized liquidity aggregation protocol Magpie Protocol was attacked due to a contract vulnerability, resulting in $129,000 being stolen from 221 wallets. The root cause is due to unchecked call data. The attacker called the contract's swap() function and passed in data which included a list of users to transfer tokens from.
