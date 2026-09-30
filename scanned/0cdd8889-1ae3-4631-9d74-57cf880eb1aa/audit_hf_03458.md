# [H] POSU-1 | willPositionCollateralBeSufficient Validation Bypassed

## Summary
Severity: High
Contest weight: 0.1534
Dataset id: 18872
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The willPositionCollateralBeSufficient validation aims to decide whether or not the collateral amount that remains for a position will be sufficient for it's leverage. However in many cases this validation allows decrease orders which will put the position’s collateral below the “sufficient threshold”. This is because the willPositionCollateralBeSufficient validation excludes fees that will be subtracted from the position's collateral as well as negative price impact that can be applied to the position's collateral.

## Recommendation
Account for fees and potentially even negative price impact in the willPositionCollateralBeSufficient so that the validation cannot be circumvented in these cases.
