# [M] No access control on assignFees

## Summary
Severity: Medium
Contest weight: 0.0584
Dataset id: 1311
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the Vault owner decides to set factoryMintFee and factoryRandomRedeemFee to zero, any user could call the function NFTXVaultFactoryUpgradeable.assignFees() and hence all the fees are updated.

This function is left over from some upgrades. It will be removed. Thank you.

**[0xKiwi (NFTX) resolved](https://github.com/code-423n4/2021-12-nftx-findings/issues/50)**

## Recommendation
No recommendation
