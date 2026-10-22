# [H] Proper Validation of Size Delta in increasePosition()

## Summary
Severity: High
Contest weight: 0.6359
Dataset id: 12646
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Future contract provides an interface, i.e., increasePosition(), for users to open new positions or increase the already existing positions. While reviewing the calculation of the size delta, we notice there is a lack of validation for the size delta to ensure the size delta cannot be 0.
To elaborate, we show below the related code snippet of the Future::increasePosition() routine. This routine accepts a notional delta, i.e., _notionalDelta, that the trader wants to increase. Based on the notional delta and the current prices of the collateral/index tokens, it calculates the corresponding position size delta, i.e., sizeDelta (line 484). The position is then updated with the new increased notional delta/size delta (lines 509 510).
However, it comes to our attention that the routine does not properly validate the size delta.
In particular, if the calculated sizeDelta is 0, the trader can keep the position size unchanged while increasing the open notional. As a result, the position is messed up and the trader may lose for a long position or get proﬁt for a short position. Accordingly, we suggest to properly validate the calculated size delta and ensure it is a valid value (not 0).
```solidity
function increasePosition(
    address _collateralToken,
    address _indexToken,
    address _account,
    bool _isLong,
    uint256 _notionalDelta
) public override nonReentrant {
    _validateRouter(_account);
    require(getPairStatus(_collateralToken, _indexToken) == PairStatus.list, "pair_unlist");
    validateLiquidate(_collateralToken, _indexToken, _account, _isLong, true);
    _updateFundingFeeRate(...);
    Position storage pos = _getPosition(_collateralToken, _indexToken, _account, _isLong);
    uint256 marginDelta = _transferIn(_collateralToken);
    uint256 sizeDelta = uint256(
        token1ToToken2(_collateralToken, int256(_notionalDelta), _indexToken)
    );
    (int256 fundingFee, uint256 tradingFee) = _calcNewPosition(
        _collateralToken,
        _indexToken,
        _account,
        _isLong,
        _notionalDelta,
        sizeDelta,
        true
    );
    _increaseTotalSize(_collateralToken, _indexToken, _isLong, sizeDelta);
    _increaseTotalOpenNotional(_collateralToken, _indexToken, _isLong, _notionalDelta);
    int256 remainMargin = int256(pos.margin) + int256(marginDelta) - fundingFee - int256(tradingFee);
    require(remainMargin > 0, "insuff_margin");
    pos.margin = uint256(remainMargin);
    pos.openNotional = pos.openNotional + _notionalDelta;
    pos.size = pos.size + sizeDelta;
    pos.entryFundingRate = getCumulativeFundingRate(_collateralToken, _indexToken, _isLong);
    pos.entryCollateralPrice = getPrice(_collateralToken);
    pos.entryIndexPrice = pos.openNotional / pos.size;
    ...
}
```
Note the same issue is also applicable to the _decreasePosition() routine where the decreased size delta cannot be 0.

## Recommendation
Properly validate the calculated size delta and ensure it is a valid value (not 0).
