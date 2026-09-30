# [M] getLiqPnlThresholdP could revert

## Summary
Severity: Medium
Contest weight: 0.5760
Dataset id: 8362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidation parameters are configured, it is possible for startLeverage and endLeverage to have the same value. This can be useful for an asset group where a constant liquidation threshold is desired, regardless of leverage. However, when getLiqPnlThresholdP is called and the provided _leverage is equal to startLeverage / endLeverage , it will revert if startLeverage equal to endLeverage due to division by 0.
```solidity
function getLiqPnlThresholdP(
    IPairsStorage.GroupLiquidationParams memory _params,
    uint256 _leverage
) public pure returns (uint256) {
    // For trades opened before v9.2, use legacy liquidation threshold
    // LEGACY_LIQ_THRESHOLD_P = 90 * P_10; // -90% pnl
    if (_params.maxLiqSpreadP == 0) return ConstantsUtils.LEGACY_LIQ_THRESHOLD_P;
    if (_leverage < _params.startLeverage) return _params.startLiqThresholdP;
    if (_leverage > _params.endLeverage) return _params.endLiqThresholdP;
    return
        _params.startLiqThresholdP -
        ((_leverage - _params.startLeverage) *
        (_params.startLiqThresholdP - _params.endLiqThresholdP)) /
        (_params.endLeverage - _params.startLeverage);
}
```

## Recommendation
Consider returning _params.startLiqThresholdP / _params.endLiqThresholdP when _leverage is equal to _params.startLeverage / _params.endLeverage .
```solidity
function getLiqPnlThresholdP(
    IPairsStorage.GroupLiquidationParams memory _params,
    uint256 _leverage
) public pure returns (uint256) {
    // For trades opened before v9.2, use legacy liquidation threshold
    // LEGACY_LIQ_THRESHOLD_P = 90 * P_10; // -90% pnl
    if (_params.maxLiqSpreadP == 0) return ConstantsUtils.LEGACY_LIQ_THRESHOLD_P;
    if (_leverage <= _params.startLeverage) return _params.startLiqThresholdP;
    if (_leverage >= _params.endLeverage) return _params.endLiqThresholdP;
    return
        _params.startLiqThresholdP -
        ((_leverage - _params.startLeverage) *
        (_params.startLiqThresholdP - _params.endLiqThresholdP)) /
        (_params.endLeverage - _params.startLeverage);
}
```
Describe your recommendation here
