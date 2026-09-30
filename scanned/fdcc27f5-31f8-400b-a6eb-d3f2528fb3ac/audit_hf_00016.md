# [H] RSKE-2 | Expired Options Increase Maintenance Margin

## Summary
Severity: High
Contest weight: 0.0821
Dataset id: 92
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the healthFactor function, the positionMaintenanceMargin is added for options which may be expired, however expired options should not increase the required margin for an account — their result is already factored into PnL and that result cannot change.

## Recommendation
Skip expired options for the positionMaintenanceMargin calculation.
