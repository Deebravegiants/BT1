# [H] Wrong reserves calculated for non-19 decimals points tokens

## Summary
Severity: High
Contest weight: 0.0948
Dataset id: 13474
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As part of `calculateFairReserves` function, a square root of each reserve is calculated and divided by 1e18 to normalized the value to 18 decimals. However, there is evidence that reserves are 18 decimals value in the first place which will result in a wrong value calculated for pairs with tokens that do not have 18 decimal points.

## Recommendation
No recommendation
