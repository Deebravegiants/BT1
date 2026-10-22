# [H] Incorrect TP/SL Order Creation/Update in OrderManager

## Summary
Severity: High
Contest weight: 0.6353
Dataset id: 12426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the order management, the LogX protocol has a built-in OrderManager contract. In the process of analyzing the order creation logic, we notice the current implementation has an improper way to create and update orders. In the following, we show the code snippet of the related createOrders() routine. This routine has a number of arguments and is defined to allow the user to create new orders. However, it comes to our attention that the new limit order has been specified with a user-controlled argument _isIncreaseOrder (line 971), which should be a constant true. Similarly, the associated TP/SL orders should have its _isIncreaseOrder with a constant false, not modified by the user either. In addition, the same TP/SL orders should also have 0 as its _collateralDelta argument.
```solidity
if(limitPrice != 0){
    uint256 currMarketPrice = _isLong? IPriceFeed(pricefeed).getMaxPriceOfToken(_indexToken) : IPriceFeed(pricefeed).getMinPriceOfToken(_indexToken);
    _validateLimitOrderPrices(currMarketPrice, _isLong, _limitPrice);
    IERC20(_collateralToken).transferFrom(msg.sender, address(this), _collateralDelta);
    uint256 _collateralAmountUsd = IUtils(utils).tokenToUsdMin(_collateralToken, _collateralDelta);
    require(_collateralAmountUsd >= minPurchaseTokenAmountUsd, "OrderManager: too less collateral");
    _createOrder(msg.sender, _collateralDelta, _collateralToken, _indexToken, _sizeDelta, _isLong, _limitPrice, !_isLong, minExecutionFeeLimitOrder, _isIncreaseOrder, _maxOrder);
} else {
    // tpsl order or limit order when closing position
    uint256 currMarketPrice = !_isLong? IPriceFeed(pricefeed).getMaxPriceOfToken(_indexToken) : IPriceFeed(pricefeed).getMinPriceOfToken(_indexToken);
    _validateTPSLOrderPrices(currMarketPrice, _isLong, _tpPrice, _slPrice);
    if(tpPrice != 0){
        _createOrder(msg.sender, _collateralDelta, _collateralToken, _indexToken, _sizeDelta, _isLong, _tpPrice, _isLong, minExecutionFeeLimitOrder, _isIncreaseOrder, _maxOrder);
    }
    if(slPrice != 0){
        _createOrder(msg.sender, _collateralDelta, _collateralToken, _indexToken, _sizeDelta, _isLong, _slPrice, !_isLong, minExecutionFeeLimitOrder, _isIncreaseOrder, _maxOrder);
    }
}
```
Moreover, the create order may be updated via a routine updateOrder(), which should be enhanced with the proper validation on the given _triggerPrice and _triggerAboveThreshold. We also notice the order update routine should not update the order's _collateralDelta without properly transferring in or out respective collateral.

## Recommendation
Revise the above routine to properly manage user orders.
