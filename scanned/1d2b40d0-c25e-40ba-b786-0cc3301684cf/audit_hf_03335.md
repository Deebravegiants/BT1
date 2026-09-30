# [M] DPCU-4 | indexToken vs pnlToken Arbitrage

## Summary
Severity: Medium
Contest weight: 0.1111
Dataset id: 18186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For markets where the pnlToken can be the same as the indexToken, there are cases where the indexToken and pnlToken are valued differently and users benefit from this difference at the market’s expense. Consider a StopLossDecrease order for a long in profit, the pnlToken is the same as the indexToken. The user's pnl calculation can value the indexToken at the acceptablePrice, say $5495. However the resulting values.positionPnlUsd is converted to the pnlToken at the secondaryPrice, say $5490. This yields a delta of tokens that was not originally factored into the PnL for the market, so the market experiences slightly more loss than expected and the user gains slightly more than expected.

## Recommendation
For cases where the pnlToken is the same as the indexToken, consider using the executionPrice to denominate the values.pnlAmountForPool.
