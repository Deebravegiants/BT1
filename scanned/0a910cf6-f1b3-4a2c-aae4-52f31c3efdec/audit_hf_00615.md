# [M] M-14 | Imprecise PnL In realizeProfit

## Summary
Severity: Medium
Contest weight: 0.1285
Dataset id: 2114
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Market._realizeProfit accepts a poolPnlUsd amount that should be realized as a profit in the collateral pool. The same poolPnlUsd is being returned from the function as deliveredPoolPnlUsd and will later be saved in the corresponding ClosePositionResult/LiquidatePositionResult struct. However, when Market_.realizeProfit() calls CollateralPool.realizeProfit, the pool recalculates the wad amount of collateral for tokens with different decimal tokens. This will cause a discrepancy between the real USD value realized as profit and the value assigned to deliveredPoolPnlUsd for tokens with less than 18 decimals. This can cause some close orders with isWithdrawProfit = true to revert because the deliveredPoolPnlUsd will be added towards the withdrawUsd that the order book will try to withdraw from the user's collateral.

## Recommendation
Recalculate the actual USD profit value based on the collateralAmount returned from CollateralPool.realizeProfit and assign that new value to deliveredPoolPnlUsd.
