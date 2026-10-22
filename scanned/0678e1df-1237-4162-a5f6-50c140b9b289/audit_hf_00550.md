# [M] M-01 | ShadowFactory Cannot Deploy NFTs

## Summary
Severity: Medium
Contest weight: 0.0641
Dataset id: 2009
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ShadowFactory is used to create shadow NFTs. It implements Ownable and has onlyOwner on deployAndRegister to prevent anyone but the owner from using this function. However, the issue is that this owner is never initialized, meaning that after deployment, the owner would be address 0 and no one would be able to call deployAndRegister.

## Recommendation
Add _initializeOwner inside the constructor, or add another function to call it and initialize it. In the second scenario, _guardInitializeOwner also needs to be called.
