# [H] Funding Fee Avoidance via Zero-Size Increase Order

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 12938
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function increasePosition(
    PosInfo calldata _posInfo
) external override nonReentrant {
    if (_tradeExt().isPaused()) revert("Trading: trading disabled");
    _validateRouter(_posInfo.account);
    // update funding fee
    _updateFundingFee(_posInfo.indexAsset, _posInfo.vault);
    bytes32 key = _getPosKey(_posInfo);
    Position storage position = positions[key];
    uint256 price = _getPrice(_posInfo, true);
    // first time opening a position
    if (position.size == 0) {
        position.averagePrice = price;
        position.indexAsset = _posInfo.indexAsset;
        position.isLong = _posInfo.isLong;
        position.vault = _posInfo.vault;
    }
    if (position.size > 0 && _posInfo.sizeDelta > 0) {
        // update average price for exists position
        position.averagePrice = getNextAveragePrice(
            position,
            price,
            _posInfo.sizeDelta
        );
    }
    // use vault uni stable token as margin asset
    if (_posInfo.sizeDelta > 0) {
        // check min position size delta
        if (_posInfo.sizeDelta < _tradeExt().minPos(_posInfo.vault)) revert("Trading: min pos size delta not met");
        // collect fee
        uint256 fee = _collectIncreasePositionFee(position, _posInfo);
        // update position
        uint256 _oriMargin = position.margin;
        position.margin += _posInfo.marginDelta;
        if (position.margin < fee) revert("Trading: margin not enough for fee");
        position.margin -= fee;
        position.entryFundingRate = _tradeExt().getAccInterest(_posInfo.indexAsset, _posInfo.vault, _posInfo.isLong);
        position.size += _posInfo.sizeDelta;
        position.lastUpdated = ChainUtils.getTime();
        if (position.size == 0) revert("Trading: position size is 0");
        _validatePosition(position.size, position.margin);
        validateLiquidation(_posInfo, true);
        // modify oi and borrow asset
        _updateOi(_posInfo, true);
        _emitIncreasePosition(key, _posInfo, price, fee, _oriMargin);
    }
}
```

## Recommendation
Revise the above routine to reliably compute and collect funding fees for each user position.
