# [M] M-03 | newRequiredMargin Uses fillPrice

## Summary
Severity: Medium
Contest weight: 0.0791
Dataset id: 22108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In getRequiredMarginWithNewPosition, newRequiredMargin is calculated with fillPrice. This is
inaccurate as fillPrice includes a premium/discount, and therefore should only be used for PnL
calculations.
Otherwise, a new position might be within the required margin (based on fillPrice) but immediately
after settling it could be eligible for liquidation (which calculates margin based on oracle price).
This is also inconsistent with how oldRequiredMargin is calculated in the next step, which uses
currentPrice.

## Recommendation
Use currentPrice to calculate newRequiredMargin.
