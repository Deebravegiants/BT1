# [M] M-07 | Underflow loanAmount Calculation

## Summary
Severity: Medium
Contest weight: 0.0476
Dataset id: 22090
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getCollateralRequirementForAdditionalTokens the loanAmount is not capped at a minimum of 0 as it is done in the updateValidLp function. This can lead to underflows if the borrowed amount plus the given increase amount is smaller than the tokensOwed.

## Recommendation
Calculate the loanAmount as it is done in the updateValidLp function to prevent underflows.
