# [M] M-4 Inconsistent Key Formats

## Summary
Severity: Medium
Contest weight: 0.1080
Dataset id: 7450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An inconsistency was found in the getGuardedValue function of the DIAOracleV2Guardian contract. The problem lies in the format of the key that is being passed to the assetRegistry.getValue(...) function. The format doesn't match the information set in the asset_registry constructor, leading to potential malfunctions. The keys set in the asset_registry constructor also contain addresses with capital letters, while toHexString function returns the string in lowercase format, containing the address, which is then used during the registry key construction. This may lead to the inability to ﬁnd the corresponding guardian key.

## Recommendation
We strongly recommend ensuring the consistency of key formats throughout all related functions and in the asset_registry constructor. Having a consistent data format could prevent possible deployment issues and ensure the smooth operation.
