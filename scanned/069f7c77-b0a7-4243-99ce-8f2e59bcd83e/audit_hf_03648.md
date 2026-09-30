# [H] First depositor can abuse exchange rate to

## Summary
Severity: High
Contest weight: 0.0941
Dataset id: 19728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Classic issue with vaults. First depositor can deposit a single wei then donate to the vault to greatly inflate share ratio. Due to truncation when converting to shares this can be used to steal funds from later depositors. See summary. First depositor can steal funds due to truncation

## Recommendation
Either during creation of the vault or for first depositor, lock a small amount of the deposit to avoid this.
