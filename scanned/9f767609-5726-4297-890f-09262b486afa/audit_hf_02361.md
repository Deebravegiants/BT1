# [H] Possible Liquidation of Healthy User Positions

## Summary
Severity: High
Contest weight: 0.6241
Dataset id: 12791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a core TradeEngine contract that is designed to execute user orders and update user positions. In particular, when a position is under water, the position may be liquidated. Our analysis on current liquidation logic indicates that a healthy user position may also be liquidated. In the following, we show the implementation of the related routine `liquidatePosition()`. As the name indicates, this routine is used to liquidate a user position. However, it comes to our attention that the given user position is not validated to meet the liquidation condition. As a result, a healthy user position may also be liquidated.
```solidity
function liquidatePosition(MarketId _id, bytes32 _positionKey, bytes32 _requestKey, address _liquidator) external onlyRoles(_ROLE_4) nonReentrant {
    IVault vault = market.getVault(_id);
    Position.Data memory position = tradeStorage.getPosition(_id, _positionKey);
    if (position.user == address(0)) revert TradeEngine_PositionDoesNotExist();
    uint48 requestTimestamp = priceFeed.getRequestTimestamp(_requestKey);
    Execution.validatePriceRequest(priceFeed, _liquidator, _requestKey);
    Execution.Prices memory prices = Execution.getTokenPrices(priceFeed, position.ticker, requestTimestamp, position.isLong, false);
    // No price impact on Liquidations
    prices.impactedPrice = prices.indexPrice;
    _updateMarketState(_id, prices, position.ticker, position.size, position.isLong, false);
    Position.Settlement memory params = Position.createLiquidationOrder(position, prices.collateralPrice, prices.collateralBaseUnit, _liquidator);
    _decreasePosition(_id, vault, params, prices);
    _liquidatePositionEvent(_id, _positionKey, position, prices.indexPrice, params.request.input.collateralDelta);
}
```

## Recommendation
Improve the above-mentioned routine to ensure only a under-water user position can be liquidated.
