# [H] H-03 | Bad Debt Incurred During Liquidate Margin

## Summary
Severity: High
Contest weight: 0.1526
Dataset id: 22080
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Accounts are determined to be eligible for liquidateMarginOnly when their availableMargin < 0, which implies that the cost of their debt has exceed the value of their collateral. The collateral discount acts as a buffer which would prevent bad debt from immediate price changes. However, there is no requirement that margin is able to cover liquidation fees. These fees will always result in bad debt which will build up in the system over time.

## Recommendation
When checking eligibility for margin liquidation in isEligibleForMarginLiquidation, subtract liquidation fees from availableMargin.
