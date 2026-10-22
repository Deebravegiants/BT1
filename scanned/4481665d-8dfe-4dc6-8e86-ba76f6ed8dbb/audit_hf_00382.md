# [M] Stop loss orders cannot be liqui-

## Summary
Severity: Medium
Contest weight: 0.4242
Dataset id: 1768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to a check that requires the liquidation price to be greater than the Stop Loss price (in the case of a buy) in the executeLimitOrder function of the Trading.sol contract, the operator cannot liquidate an order if the stop loss is higher than the liquidation price, even when the trade is liquidatable due to sudden price moves or gaps. This check should only apply to guaranteed Stop Loss (SL) orders. Currently, however, it is also applied to non-guaranteed orders, making them unliquidatable in these cases.
Incorrect check in Trading.sol:522
```solidity
require(t.sl == 0 || (t.buy ? liqPrice > t.sl : liqPrice < t.sl), "HAS_SL");
```
This check should only be done for pairs with guaranteed stop loss.
Internal pre-conditions
Gap down or gap up or sudden price move
External pre-conditions
Attack Path
1. Trader open XYZ long at 500.
2. Set his stop loss to 450 and his liquidation price is 400.
3. XYZ is a commodity which got opened at a gap down price the later day at 395.
4. The traders position is now liquidatable because current price of XYZ is less than the liquidation price of 400. But it cannot be liquidated by the operator because of the above mentioned check and it can only be closed using a stop-loss limit close.
Positions can’t be liquidated even if they are in the liquidation stage.

## Recommendation
Do that check only for stop loss guaranteed stop loss pairs
