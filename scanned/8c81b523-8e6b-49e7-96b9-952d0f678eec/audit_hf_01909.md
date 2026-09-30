# [M] BasicVault is incompatible with fee-on-transfer tokens

## Summary
Severity: Medium
Contest weight: 0.0562
Dataset id: 10502
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit and redeem functions of the vault take an amount parameter and mint/burn the
corresponding amounts assuming a 1:1 ratio. However, fee-on-transfer tokens charge a
small fee on every transfer, disrupting the 1:1 ratio and causing issues with internal
accounting.

## Recommendation
Compute the balance before and after the transfer, then subtract them to get the actual
amount transferred. Additionally, use the nonReentrant modifier to prevent reentrancy in
ERC777 tokens.
