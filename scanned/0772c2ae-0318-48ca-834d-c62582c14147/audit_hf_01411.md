# [M] Unsafe type-casts

## Summary
Severity: Medium
Contest weight: 0.0672
Dataset id: 7240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unsafe type-casts are performed throughout the contracts.
• HyperdriveLong.sol#L259
• HyperdriveLong.sol#L321
• HyperdriveLP.sol#L157
• HyperdriveLP.sol#L320-L321
• HyperdriveLP.sol#L352
• HyperdriveLP.sol#L418
• HyperdriveLP.sol#L418-L441
• HyperdriveLP.sol#L532-L536
• HyperdriveShort.sol#L360
• FixedPointMath.sol#L145
• HyperdriveMath.sol#L388-L389
• HyperdriveMath.sol#L477-L484

## Recommendation
We recommend using safe type-casts that check if the value fits into the new type's range as the default.
