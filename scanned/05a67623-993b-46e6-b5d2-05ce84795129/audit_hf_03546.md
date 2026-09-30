# [M] GLPM-5 | Reduced Burn Fee Can Be Larger Than Current

## Summary
Severity: Medium
Contest weight: 0.0702
Dataset id: 19348
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX is choosing to reduce the burn fee to further incentivize migration from GMX V1 to its latest GMX V2 system. However, there is no guarantee that the reducedMintBurnFeeBasisPoints is less than or equal to the current mintBurnFeeBasisPoints. The burn fee can be increased to be larger than its current value, causing users to redeem less tokens than expected.

## Recommendation
Inside modifier withReducedRedemptionFees, only update the burn fee in GMX V1 if the _reducedMintBurnFeeBasisPoints is smaller: bool shouldUpdateFees = _reducedMintBurnFeeBasisPoints < mintBurnFeeBasisPoints;
