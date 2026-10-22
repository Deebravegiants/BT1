# [M] M-01 | ClosePosition Only Updates The Current Market’s Borrowing Fee

## Summary
Severity: Medium
Contest weight: 0.1276
Dataset id: 2118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is closed, the contract updates only the borrowing fees for the currently closed market before verifying maintenance margin safety. This means that the margin check is performed without considering the borrowing fees pending to be paid in other still open markets. As a result, once all borrowing fees eventually get updated for those other markets, the position may fall below the required maintenance margin and become liquidatable. This could allow users to close a position on one market and leave the account appearing safe at the time of closure, despite actually being unsafe once all borrowing fees are updated. Moreover, it also allows users to close a position that could be in a liquidated state but appears safe because the borrowing fees were not applied in the other markets.

## Recommendation
Update all relevant market borrowing fees before performing the maintenance margin check by calling the _updateBorrowingForAllMarkets function so that the position’s true value is evaluated.
