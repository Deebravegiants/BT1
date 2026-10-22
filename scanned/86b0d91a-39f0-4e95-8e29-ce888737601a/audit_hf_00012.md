# [C] DIEM-2 | Sell Premium Paid Twice

## Summary
Severity: Critical
Contest weight: 0.1565
Dataset id: 83
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the openTrades function, when a user opens a !isBuy trade their portfolio receives the totalPremium immediately. However upon settling and closing the expired trade, when the premium of the expired option is 0 the _trade.averageEntry.mulDivUp(closedUnits, 1e18), which represents the totalPremium upon opening the sell trade, is credited as PNL in the _calculatePnl function and later transferred to the user’s portfolio a second time.

## Proof of Concept
https://github.com/GuardianAudits/IVX-Suite/blob/main/test/guardian/DIEM-2.sol

## Recommendation
Do not credit the initial totalPremium as PNL when the sell trade is closed as this amount has already been paid out.
