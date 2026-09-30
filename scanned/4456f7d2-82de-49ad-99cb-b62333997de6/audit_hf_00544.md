# [M] M-02 | Incompatible Types

## Summary
Severity: Medium
Contest weight: 0.0483
Dataset id: 2002
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A VestingConfig object contains uint256 streamId but the VestingConfigStorage contains uint8 streamId. Consequently, some user configurations will be unclaimable when the uint256 type is cast to uint8 within _saveClaimParameters, as it will revert with error Overflow().

## Recommendation
Consider keeping types consistent or clearly document this behavior.
