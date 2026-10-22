# [H] Improper Increase Position Cancellation in OrderManager

## Summary
Severity: High
Contest weight: 0.6326
Dataset id: 12428
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The new increase order creation may come with the creation of associated new TP/SL/maxTP orders. In the process of analyzing their execution fee, we notice the current fee collection logic may expose a vulnerability to drain funds in OrderManager. In the following, we show the implementation of the createIncreasePosition() routine. This routine is designed to create an increase position order. Based on the given arguments, it will also create a maxTP order as well as possibly two other TP/SL orders. We notice both TP/SL orders may be collected with the so-called minExecutionFeeLimitOrder fee while the creation of maxTP order is mandatory, but without the minExecutionFeeLimitOrder fee. However, its cancellation may always refund the order creator with the minExecutionFeeLimitOrder fee.
```solidity
uint256 collateralAmount = _amountIn;
bool isLong = _isLong;
address collateralToken = _collateralToken;
address indexToken = _indexToken;
uint256 sizeDelta = _sizeDelta;
tpPrice = IUtils(utils).getTPPrice(_sizeDelta, true, _acceptablePrice, collateralAmount * maxProfitMultiplier, collateralToken);
_createOrder(msg.sender, 0, collateralToken, indexToken, sizeDelta, isLong, tpPrice, isLong, minExecutionFeeLimitOrder, false, true);
return positionKey;
}

function _cancelOrder(bytes32 orderKey, uint256 _orderIndex, Order memory order) internal {
    require(order.account != address(0), "OrderManager: non-existent order");
    delete orders[orderKey];
    EnumerableSet.remove(orderKeys, orderKey);
    if(order.isIncreaseOrder){
        IERC20(order.collateralToken).transfer(order.account, order.collateralDelta);
    }
    (bool success, ) = (order.account).call{value: order.executionFee}("");
    require(success, "OrderManager: Exectuion Fee transfer failed");
}
```
Moreover, we may need to revisit the order cancellation logic to cancel the associated TP/SL/maxTP orders if the base increase position order is cancelled.

## Recommendation
Revise the above routine to properly refund user fee only if the fee is collected.
