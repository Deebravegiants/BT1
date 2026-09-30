# [M] M-05 | entryPrice Used To Validate Initial Margin

## Summary
Severity: Medium
Contest weight: 0.1078
Dataset id: 21113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateNextPositionIm function the getLiquidationMarginUsd function is used to compute the initial margin value that the position must uphold. However the initial margin value is computed based upon the newPosition.entryPrice rather than the oraclePrice. This is in direct contradiction to the price used to calculate and validate the maintenance margin for the position in the validateNextPositionEnoughMargin function, which uses the oraclePrice. This leads to a discrepancy in the validation performed on a position when validating a trade. The initial margin is validated based upon the entryPrice while the maintenance margin is validated based upon the oraclePrice.

## Recommendation
In the validateNextPositionIm function, call getLiquidationMarginUsd with the oraclePrice instead of entryPrice.
