# [M] M-09 | Empty Collateral Can Be Activated

## Summary
Severity: Medium
Contest weight: 0.1638
Dataset id: 2109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Market._realizeProfit() calls CollateralPool.realizeProfit which charges a given amount of the pool's collateral token from the LPs in order for the trader to be paid. After that, the charged collateral token is added towards the activeCollaterals of that trader. This is done regardless of the charged amount. Because CollateralPool.realizeProfit converts from USD to the collateral token and divides multiple times, it's possible to have positive PnL in USD, but the result in collateral token to be 0. When this happens, LPs won't be charged and the trader won't profit, but the collateral token of the pool will still be added to their activeCollaterals. This will result in users having tokens with 0 balance in their activeCollaterals, which:
• Increases unnecessarily their collateral tokens count, making it harder to add new tokens.
• Can block the fulfilment of a close order which withdraws USD because withdrawUsd goes over each active collateral and tries to withdraw from it by passing the needed amount to _withdrawFromAccount. Inside that internal function there is a require assertion that will revert the transaction if the amount is 0.

## Recommendation
In Market._realizeProfit add the collateralToken to activeCollaterals only if collateralAmount is not 0.
