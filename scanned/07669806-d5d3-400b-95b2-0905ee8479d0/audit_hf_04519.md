# [H] H-06 | Liquidations Errantly Adjust DebtCorrection

## Summary
Severity: High
Contest weight: 0.1709
Dataset id: 22083
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PoC When there is not enough liquidation capacity left, position liquidations will be done in multiple transactions while the account liquidation will occur in the first transaction. In every subsequent liquidation for the position, the debtCorrectionAccumulator will be updated with the latest funding accrued for the fundingDelta and fundingPnl, however as the position does not realize the funding changes from the period [flagPosition, liquidatePosition], this debtCorrectionAccumulator adjustment is invalid. As a result the reportedDebt of the market is perturbed.

## Recommendation
In the case of a liquidation of a position which was previously flagged, do not use the latest funding changes that took place after the position’s flagging to adjust the fundingPnl value as this amount will not be realized to the account’s margin.
