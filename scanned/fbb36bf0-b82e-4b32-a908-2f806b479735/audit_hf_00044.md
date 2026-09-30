# [H] RSKE-1 | Borrowing Fees Accounted For Twice

## Summary
Severity: High
Contest weight: 0.1308
Dataset id: 120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The borrowing fees are included in the maintenanceMarginForPositions which is the numerator for the health factor. However the borrowing fees are also deducted from the PnL of the position in the calculatePnl function, therefore reducing the denominator of the health factor. Therefore the effect of the borrowing fees is doubled when determining the health factor of positions, leading to positions being errantly liquidated.

## Recommendation
Adjust the PnL of a trade such that it does not include the borrowing fee, or remove the borrowing fees from the maintenanceMarginForPositions.
