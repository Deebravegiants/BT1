# [M] Double Performance Fee on Donations

## Summary
Severity: Medium
Contest weight: 0.1055
Dataset id: 2642
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a token without an oracle is donated, it's treated as a donation without fees. Later, when an oracle is mapped to the token, internalizing the donation incorrectly applies the performance fee a second time, reducing the escrowed funds twice. edCollateralVault.sol#L109 edCollateralVault.sol#L244 Duplicate Fee Logic: Fees are applied during both donation and internalization. Internal Pre-conditions External Pre-conditions Attack Path without oracle harvested without an oracle mapped. Map Oracle: Oracle is assigned Internalize Donation: Protocol processes the donation again. Apply Fee Twice: Performance fees are deducted both during donation and internalization. double fee applied reducing harvest

## Recommendation
dont apply fee for token with no oracle mapped
