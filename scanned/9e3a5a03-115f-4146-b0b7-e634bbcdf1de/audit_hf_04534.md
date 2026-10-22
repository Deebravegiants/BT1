# [M] M-15 | Fill Price Funding And Interest Discrepancy

## Summary
Severity: Medium
Contest weight: 0.1182
Dataset id: 22098
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _settleOrder and updatePositionData, oldPosition's PnL is called with fillPrice, which computes
funding and interest based on fillPrice.
This is problematic for two reasons:
a) it causes a discrepancy with recomputeFunding which uses oraclePrice (see AsyncOrder.sol:
289).
b) Funding and interest should not be based upon fillPrice, as this price includes a
premium/discount according to how the trade affects the market skew.
As a result, shorts pay more fees when they balance the market and less when they imbalance the
market. Consider this scenario:
• order price = 1000
• short trade (positive price impact), fill price = 1010 => more fees are paid
• short trade (negative price impact), fill price = 990 => less fees are paid

## Recommendation
Consider changing to use oraclePrice in these two areas:
1. _settleOrder: oldPosition.getPnl(runtime.fillPrice)
2. updatePositionData: oldPosition.getPnl(runtime.currentPrice)
