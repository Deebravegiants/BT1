# [M] M-08 | getFillPrice And validateLiquidation Revert Due To Division By 0

## Summary
Severity: Medium
Contest weight: 0.0561
Dataset id: 21126
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If skewScale is set to 0, arithmetic operations which divide by skewScale will revert. This occurs in the Order.getFillPrice and Position.validateLiquidation functions. While it is unlikely that skewScale will ever be set to 0, this is a possibility and is specifically handled in many areas of the codebase.

## Recommendation
In getFillPrice and validateLiquidation handle the scenario for skewScale == 0 and avoid division by 0.
