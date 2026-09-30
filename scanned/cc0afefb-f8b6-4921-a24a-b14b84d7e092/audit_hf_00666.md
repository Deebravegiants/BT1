# [M] M-13 | Token Losses On Deposit

## Summary
Severity: Medium
Contest weight: 0.0936
Dataset id: 2202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can use Vault._deposit() to deposit tokens from the vault side to the ledger side. They will be charged an amount of these tokens on the vault side. Since this token may have different decimal precision on each chain, the amount added towards the user balance on the ledger side is adjusted by convertDecimal. In case srcDecimals > dstDecimals, the amount will be divided to convert it to dstDecimals and the rest will be lost. This adjusted amount will also be recorded in the vaultManager for the given srcChainId. In result, users will lose part of their tokens.

## Recommendation
Consider adding a convertDecimal function to the Vault as well and charging the user the newly adjusted amount.
