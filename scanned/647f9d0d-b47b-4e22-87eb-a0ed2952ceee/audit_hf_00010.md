# [C] LP-1 | Required Margin Miscalculated

## Summary
Severity: Critical
Contest weight: 0.1331
Dataset id: 80
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When computing the position maintenance margin required, the maintenance margin is miscalculated because the positionMaintenanceMargin is called with the option premium as the spot price of the asset and the spot price of the asset as the option premium. This drastically miscalculates the required positionMaintenanceMargin and results in an invalid utilizationRatio, causing inflated or insufficient interest rates and undermines the maxUtilizationRatio validation.

## Recommendation
Provide the spot price as the X value and the premium as the Y value.
