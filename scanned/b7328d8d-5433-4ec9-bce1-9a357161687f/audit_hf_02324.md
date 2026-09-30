# [H] Revisited Validation of maxLeverage in decreaseMargin()

## Summary
Severity: High
Contest weight: 0.6375
Dataset id: 12645
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Perpetual protocol allows users to trade perpetual futures within the maximum allowed leverage. Any operation that may exceed the max leverage is forbidden. While reviewing the margin decrease via the _decreasePosition()/decreaseMargin() routines, we notice they do not properly check if the new leverage has exceeded the maximum leverage or not.
To elaborate, we show below the code snippet of the Future::decreaseMargin() routine. The routine calculates the funding fee and the PnL ﬁrst (line 412), and gets the left margin in the position (line 414). Then it updates the new margin/openNotinal of the position (lines 417 418) and transfers the margin delta to the user in the positionSettlement() routine (line 423).
After the update of the margin/openNotinal, the leverage also changes. However, it comes to our attention that it does not properly check if the new leverage exceeds the max leverage or not. As a result, the user can still decrease margin from a position where the new leverage may exceed the max leverage.
At the end of the routine, we notice it checks whether the new position can be liquidated or not by calling the validateLiquidate() routine (line 428), which ensures the new margin ratio cannot exceed the maintenance margin ratio. However, it cannot ensure the new leverage is in the allowed range even the new position cannot be liquidated. With that, we suggest to validate the new leverage at the end of the decreaseMargin() routine.
Note the same issue is also applicable to the _decreasePosition() routine.
```solidity
function decreaseMargin(
    address _collateralToken,
    address _indexToken,
    address _account,
    bool _isLong,
    uint256 _marginDelta,
    address _receiver
) external override nonReentrant {
    _validateRouter(_account);
    require(_account == _receiver, "Invalid caller");
    validateLiquidate(_collateralToken, _indexToken, _account, _isLong, true);
    _updateFundingFeeRate(_collateralToken, _indexToken, _isLong, 0, 0);
    bytes32 posKey = getPositionKey(_collateralToken, _indexToken, _account, _isLong);
    Position storage pos = _getPosition(_collateralToken, _indexToken, _account, _isLong);
    _validatePositionExist(pos);
    (int256 fundingFee, int256 pnl) = _calcNewPosition(...);
    uint256 leftMargin = uint256(int256(pos.margin) - fundingFee + pnl);
    require(leftMargin > _marginDelta, "margin_delta_exceed");
    pos.margin = leftMargin - _marginDelta;
    pos.openNotional = uint256(token1ToToken2(_indexToken, int256(pos.size), _collateralToken));
    pos.entryFundingRate = getCumulativeFundingRate(_collateralToken, _indexToken, _isLong);
    pos.entryCollateralPrice = getPrice(_collateralToken);
    pos.entryIndexPrice = pos.openNotional / pos.size;
    positionSettlement(...);
    emit DecreaseMargin(...);
    emit UpdatePosition(...);
    // todo replace validatePosition, validate max usd per position
    validateLiquidate(_collateralToken, _indexToken, _account, _isLong, true);
}
```

## Recommendation
Properly validate the new leverage of the position at the end of the decreaseMargin() routine, and ensure it does not exceed the max allowed leverage.
