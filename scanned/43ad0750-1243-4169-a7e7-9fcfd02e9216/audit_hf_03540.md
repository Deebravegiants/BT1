# [H] ATPH-1 | Incorrect Decimals

## Summary
Severity: High
Contest weight: 0.1308
Dataset id: 19340
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the calAverageEntryPrice function is called during a liquidation or ADL execution, the liquidationQuoteDiff has 6 decimals of precision. Therefore the resulting quoteDiff on line 72 has 14 decimals of precision. This differs from the quoteDiff decimals of 16 when uploading a trade. Therefore the averageEntryPrice and openingCost values are perturbed when the quoteDiff is used to calculate the average entry during a liquidation or ADL.

## Recommendation
Adjust the quoteDiff during liquidation or ADL such that it has the expected 16 decimals of precision.
