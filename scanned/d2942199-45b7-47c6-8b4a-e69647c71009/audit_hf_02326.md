# [M] Improved Calculation of New Margin in validateLiquidate()

## Summary
Severity: Medium
Contest weight: 0.4612
Dataset id: 12647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Perpetual protocol, the Future contract timely checks if the position can be liquidated or not before each trading operation. If the position can be liquidated, it refuses any trading operation except for the liquidation on the position. While reviewing the logic to check if the position can be liquidated or not, we notice it makes use of wrong parameters values to calculate the remain margin and the margin ratio of the position.
In the following, we show the related code snippets of the validateLiquidate()/_calcNewPosition() routines. As the name indicates, the validateLiquidate() routine is used to check if the given position can be liquidated or not. It calls the _calcNewPosition() routine (line 1086) to calculate the current remain margin and the current margin ratio of the position. If the remain margin is smaller than 0 or if the margin ratio is smaller than the maintenance margin ratio of the position, the position should be liquidated.
In the _calcNewPosition() routine, it uses the _notionalDelta parameter to calculate the trading fee for the current trading and uses the _sizeDelta parameter to calculate the trading fee rate. In the validateLiquidate() routine, it calls the _calcNewPosition() routine by taking the open notional (pos.openNotional) as the value of the _notionalDelta parameter (line 1091) and the position size (pos.size) as the value of the _sizeDelta parameter (line 1092). However, it comes to our attention that the validateLiquidate() is a read-only routine that will not impact the open notional or the position size. So it shall not charge any trading fee for the validation and our analysis shows that it shall take 0 as the values of both the _notionalDelta/_sizeDelta parameters in the call to the _calcNewPosition() routine.
```solidity
function validateLiquidate(
    address _collateralToken,
    address _indexToken,
    address _account,
    bool _isLong,
    bool _raise
) public view override returns (bool shouldLiquidate) {
    bytes32 posKey = getPositionKey(_collateralToken, _indexToken, _account, _isLong);
    Position storage pos = positions[posKey];
    if (pos.size == 0) {
        return false;
    }
    (, , , int256 remainMargin, int256 marginRatio) = _calcNewPosition(
        _collateralToken,
        _indexToken,
        _account,
        _isLong,
        pos.openNotional,
        pos.size,
        false
    );
    if (remainMargin < 0) {
        shouldLiquidate = true;
        if (_raise) {
            revert("should_liquidate");
        }
    } else {
        uint256 mantainanceMarginRatio = IFutureUtil(futureUtil).getMaintanenceMarginRatio(
            _collateralToken,
            _indexToken,
            _account,
            _isLong
        );
        if (marginRatio < int256(mantainanceMarginRatio)) {
            shouldLiquidate = true;
            if (_raise) {
                revert("should_liquidate");
            }
        }
    }
}
function _calcNewPosition(
    address _collateralToken,
    address _indexToken,
    address _account,
    bool _isLong,
    uint256 _notionalDelta,
    // for trading fees
    uint256 _sizeDelta,
    bool _isIncreasePosition
    // if is increasing, calc funding fee for _notionalDelta
) private view returns (
    int256 fundingFee,
    uint256 tradingFee,
    int256 pnl,
    int256 remainMargin,
    int256 marginRatio
) {
    bytes32 posKey = getPositionKey(_collateralToken, _indexToken, _account, _isLong);
    Position storage pos = positions[posKey];
    tradingFee = calculateTradingFee(_collateralToken, _indexToken, _isLong, _notionalDelta, _sizeDelta, _isIncreasePosition);
    fundingFee = calculateFundingFee(
        _collateralToken,
        _indexToken,
        pos,
        _isLong,
        _notionalDelta,
        _isIncreasePosition
    );
    ...
}
```

## Recommendation
Revisit the validateLiquidate() routine and take 0 as the values of both the _notionalDelta/_sizeDelta parameters in the call to the _calcNewPosition() routine.
