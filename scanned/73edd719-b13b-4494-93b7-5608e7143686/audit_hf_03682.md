# [M] Adversary can DOS vault repayments by mak-

## Summary
Severity: Medium
Contest weight: 0.0720
Dataset id: 19775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
payBackToken will revert if the repayment amount is greater than the amount of debt owed by the vault. Adversary can DOS repayments by making a dust payment and causing a revert.
ol#L261-L273
VoltaVault#payBackToken requires that the repayment amount is less than or equal to the amount of debt owed by the vault. This can be frontrun with dust repayment to cause repayment to revert.
Adversary can prevent repayment

## Recommendation
If repayment amount is greater than vault debt, reduce the repayment amount to the amount owed by the vault
