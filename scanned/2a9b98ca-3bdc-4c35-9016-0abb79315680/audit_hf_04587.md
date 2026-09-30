# [M] M-20 | FraxVault Incompatible With Non-Standard Tokens

## Summary
Severity: Medium
Contest weight: 0.0552
Dataset id: 22190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FraxlendPair contracts do not support non-standard tokens such as rebasing or fee-on-transfer tokens, whose balance changes during transfers or over time. If the Peapods team expects to support these tokens, then there will be accounting issues when interacting with FraxlendPair contracts.

## Recommendation
Verify the amount of tokens transferred to the contracts before and after the actual transfer to infer any fees/interest.
