# [H] Revisited Deficit Loss Payment in PositionManager::liquidatePosition()

## Summary
Severity: High
Contest weight: 0.6349
Dataset id: 13139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Symmetry protocol, the PositionManager contract is designed to manage the user's LONG/SHORT position. In particular, the liquidatePosition() routine is designed to liquidate the user's position. While examining its logic, we observe its current implementation needs to be improved. To elaborate, we show below the related code snippet of the PositionManager contract. Inside the liquidatePosition() routine, it firstly closes the liquidated position (line 345). Next, if the position's current margin is negative, the deficit will be paid by the protocol insurance and/or LPs (lines 349-355). However, we notice the returned currentMargin (i.e., portfolio margin) (line 349) is shared by all the positions of the user rather than the liquidated position. That is to say, it may pay the deficit for the user's open position, which is against the protocol design and user expectation.
```solidity
function liquidatePosition(address _account, address _token, bytes[] calldata _priceUpdateData) external payable {
    IMarket market_ = IMarket(market);
    // update oracle price
    if (_priceUpdateData.length > 0) {
        IPriceOracle(market_.priceOracle()).updatePythPrice{value: msg.value}(msg.sender, _priceUpdateData);
    }
    // update fees
    market_.updateFee(_token);
    // validate liquidation
    require(isLiquidatable(_account), "PositionManager: account is not liquidatable");
    // compute liquidation price
    (int liquidationPrice, int size, int notionalLiquidated) = market_.computePerpLiquidatePrice(_account, _token);
    // close position
    market_.trade(_account, _token, size, liquidationPrice);
    // update global info
    market_.updateTokenInfo(_token);
    // post trade margin
    (, int currentMargin, ) = market_.accountMarginStatus(_account);
    // fill the exceeding loss from insurance account
    int deficitLoss;
    if (currentMargin < 0) {
        deficitLoss = -currentMargin;
        _coverDeficitLoss(_account, deficitLoss);
    }
}
```

## Recommendation
Properly pay the deficit for the liquidated position.
