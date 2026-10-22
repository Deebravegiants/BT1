# [M] DIEM-6 | PNL Always Decreased By borrowedAmount

## Summary
Severity: Medium
Contest weight: 0.0995
Dataset id: 96
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _calculatePnl function, for expired buy trades the PNL is decreased by the entire borrowedAmount no matter the closedUnits provided. This is fine during the _closeTrade function call as the _amountContracts is set to the entire trade.contractsOpen, however other functions that rely on the _calculatePnl function do not make this adjustment. For example the calculatePnl function does not make such an adjustment and therefore can give results that may be used to manipulate systems interacting with IVX and relying on the returned value.

## Recommendation
Replace structured.PNL -= int256(_trade.borrowedAmount) with structured.PNL -= int256(_trade.borrowedAmount.mulDivUp(closedUnits, _trade.contractsOpen)). Otherwise make the closedUnits = _trade.contractsOpen adjustment when the option is expired in the calculatePnl view function.
