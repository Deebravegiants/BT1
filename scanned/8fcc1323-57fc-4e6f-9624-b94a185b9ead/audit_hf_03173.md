# [M] Underlying With Non-Standard Decimals Not

## Summary
Severity: Medium
Contest weight: 0.0616
Dataset id: 17735
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Arithmetic operations are performed with the assumption that the token always has 18 decimals. LiquidationAccountant.claim Arithmetic operations assume the token has 18 decimals. Not all tokens use 18 decimals, such as Tether. • The addition of underlying capital that does not use 18 decimals will not be possible.

## Recommendation
• Consider whether the addition of capital that does not use 18 decimals is desirable in the future. If it is, refactor contracts to support tokens with non-standard decimals.
