# [H] ORDM-5 | Impossible to Liquidate When Fee is Greater Than PnL

## Summary
Severity: High
Contest weight: 0.5776
Dataset id: 20550
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _liquidatePosition function the PnlRealized event is emitted which includes the pnlInCollateral. This is calculated by taking the netPnl and subtracting feesInCollateral. However, the feesInCollateral may be greater than netPnl, causing an underflow revert.
```solidity
emit PnlRealized(_positionId, false, netPnl - feesInCollateral, feesInCollateral, executionPrice);
```
In the _getNetProfitOrLossIncludingFees function which is called in _liquidatePosition, if the position is in profit excluding fees it will enter the inner if-statement the isNetProfit will be set to false and feesInCollateral will be greater than netPnl. At the end of the _liquidatePosition function when the PnlRealized event is emitted the transaction will revert, making any liquidation impossible until the position is completely underwater, leading to a loss of yield for the protocol and LP's.

## Recommendation
Since netPnl and fees will be a loss for the position and go to the feeManager anyway, do not emit an event where netPnl - feesInCollateral is being calculated. Instead, have a separate event for liquidations where only the netPnl is being emitted.
