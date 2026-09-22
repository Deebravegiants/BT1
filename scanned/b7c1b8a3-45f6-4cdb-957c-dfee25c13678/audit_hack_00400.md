# [M] Royal.io incident: A legacy royalties contract (Royal1155LD) associated with Royal.io on Polygon was exploited due to a logic flaw in reward/pro-rata

## Summary
Severity: Medium
Target: Royal.io
Loss: $ 263,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-23
Source: https://cryptorank.io/news/feed/c9d17-legacy-polygon-royalties-contract-exploit-drains-261k-through-reward-logic-flaw
Type: slowmist-incident

## Details
A legacy royalties contract (Royal1155LD) associated with Royal.io on Polygon was exploited due to a logic flaw in reward/pro-rata royalty accounting. The attacker used a flash loan and 100 zero-value ERC1155 transfers to manipulate the beforeLdaTransfer function, inflating balances and withdrawing ~$263K USDC.
