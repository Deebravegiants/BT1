# [M] Error in OstiumPairsStorage::groupMaxCollateral() calculation

## Summary
Severity: Medium
Contest weight: 0.0894
Dataset id: 11138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculation of the maximum deposited collateral per group, erroneously divides by 100, assuming it refers to 100%. However, the maxCollateralP variable, specified here, has a precision of 2 decimals. This means that 100% is expressed as 100_00. This discrepancy results in incorrect checks in OstiumTradingCallbacks::withinExposureLimits(), potentially causing the vault's collateral to be capped at a much larger amount than intended. Furthermore, this miscalculation may dilute the reported profits.

## Recommendation
To avoid errors related to magic numbers, utilize constants for precision. Additionally, if using 100_00 to denote 100% consistently, it's preferable to adhere to Basis Point (BPS) denomination.
