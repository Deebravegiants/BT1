# [M] SPRU-1 | Double Counting Swap Imbalance

## Summary
Severity: Medium
Contest weight: 0.0785
Dataset id: 18192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the price impact USD value for a swap, the thresholdPriceImpactUsd is based on the params.usdDeltaForTokenA.abs() and params.usdDeltaForTokenB.abs(). However these values will always have the same magnitude during a swap, therefore the user’s swap USD value will be double counted. If the configured thresholdImpactFactorForVirtualInventory is intended to be 70% of the user’s swap USD value, it will instead account for 140% of the user’s swap USD value.

## Recommendation
Only base the thresholdPriceImpactUsd on a single token side of usdDelta for swaps.
