# [M] Missing whenNotPaused

## Summary
Severity: Medium
Contest weight: 0.0531
Dataset id: 1531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LensHub.sol#L929](https://github.com/code-423n4/2022-02-aave-lens/blob/main/contracts/core/LensHub.sol#L929)  

All the external function of LensHub have whenNotPaused modifier.  
However, LensHub is erc721 and the transfer function doesn’t have the whenNotPaused modifier.

## Recommendation
Add whenNotPaused to `_beforeTokenTransfer`.

Nice! Addressed in [aave/lens-protocol#75](https://github.com/aave/lens-protocol/pull/75).
