# [M] M-24 | Bad Debt Not Handled In Validate Withdraw

## Summary
Severity: Medium
Contest weight: 0.0627
Dataset id: 160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Validate Withdraw decreases the balance of the vault by the calculated assetToTransferAfterFees amt and does not cap it at zero. Therefore if this amt is bigger than the _balanceVault (for example as bad debt was taken between init and validate) an underflow occurs which leads to a long term DoS as this is a validation function.

## Recommendation
Handle bad debt in the validate withdraw function. For example, this can be done by capping assetToTransferAfterFees to s._balanceVault to avoid an underflow.
