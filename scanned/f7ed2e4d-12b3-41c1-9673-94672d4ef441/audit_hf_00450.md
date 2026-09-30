# [M] Pools TP orders doesn't prioritize

## Summary
Severity: Medium
Contest weight: 0.5890
Dataset id: 1874
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
WasabiLongPool::closePosition is used together with user signed order ClosePositionOrder to execute a Stop Loss, or Take Profit user orders.
```
The problem in WasabiLongPool is that we don't prioritize user profit for his TP order and instead check if the total amount receive from the swap is above user provided _order.takerAmount. But the following may result in close order, where user profit is less than a moment in the past, when order was still active:
```solidity
uint256 actualTakerAmount = closeAmounts.payout + closeAmounts.closeFee + closeAmounts.interestPaid + closeAmounts.principalRepaid;

// For Longs, the whole collateral is sold, so the order.takerAmount is the limit amount that the trader expects

// TP: Must receive more than or equal to order.takerAmount
// SL: Must receive less than or equal to order.takerAmount
if (_order.orderType == 0) { // Take Profit
    if (actualTakerAmount < _order.takerAmount) revert PriceTargetNotReached();
} else if (_order.orderType == 1) { // Stop Loss
    if (actualTakerAmount > _order.takerAmount) revert PriceTargetNotReached();
} else {
    revert InvalidOrder();
}
```
Imagine the following scenario:
1. User has opened USDC/WETH long position X4 with 1000 USDC down payment (assume 1 WETH = 2K USDC)
2. User has created TP order with takerAmount == 4500
3. WETH price has increased 5% and user PnL is now ($+400 -> position value is worth = 4400 USDC)
4. Some time passes and weth price isn't moving, but interested for user is accrued. Also borrow rate is high -> interest is high
5. After some weeks WETH price increases another 2% and now total position value is worth > 4500 USDC, but user payout would be less than his PnL at 3., because interest has increased at larger scale than weth price.
into account the accrued interest, but not the close fee + execution price.

## Recommendation
Consider using order's takerAmount amount as ”user profit” and compare it against closeAmounts.payout, when we have _order.orderType == 0 (Take Profit)
