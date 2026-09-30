# [M] M-15 | Wrong Pause Check For Liquidations

## Summary
Severity: Medium
Contest weight: 0.0996
Dataset id: 2115
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OrderBook.liquidate() liquidates a user by closing their position for a given market and potentially withdrawing their collateral if their MM is above their margin balance. This allows the Broker to keep the market in a healthy state. Currently, OrderBook.liquidate() will execute the whenNotPaused modifier and revert if LiquidityOrder is paused. LiquidityOrder has nothing to do with liquidate even though their names are similar. In result, if the market has the liquidity orders paused to manage some type of risk, the broker won't be able to liquidate position accounts.

## Recommendation
Consider removing the whenNotPaused modifier from OrderBook.liquidate(). There is already a _marketDisableTrade() in FacetClose.liquidatePosition() which will stop the liquidation if this is a desirable feature.
