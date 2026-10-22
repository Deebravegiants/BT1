# [M] No Incentive to Liquidate Bad Debt Due to Zero Fees

## Summary
Severity: Medium
Contest weight: 0.0630
Dataset id: 4241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current calculation results in zero fees for liquidating accounts with bad debt. This removes any incentive for liquidators to act, meaning that positions where debt exceeds collateral will not be cleared. Over time, these bad debt positions will continue to deteriorate, increasing protocol risk.

## Recommendation
• Remove the conditional logic that prevents fees from being paid when debt exceeds collateral. Always pay feeInDebt.
• Track when fees exceed remainingCollateral and replenish the transmuter from a DAO security fund when necessary.
