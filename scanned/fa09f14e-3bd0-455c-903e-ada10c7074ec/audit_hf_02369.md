# [M] Incorrect Average Price Update Logic in MarketUtils

## Summary
Severity: Medium
Contest weight: 0.4460
Dataset id: 12808
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a key Positions contract that allows the user to create or adjust his/her trading positions. While examining the current position-related logic, we notice the price adjustment of an increased position can be improved. To elaborate, we show below the code snippet from the related calculateWeightedAverageEntryPrice() routine from MarketUtils. As the name indicates, this routine computes the next average price when a position is adjusted with _sizeDelta (line 380). Specifically, for current position of _prevPositionSize with its _prevAverageEntryPrice, if it is increased by _sizeDelta with the latest mark price _indexPrice, the next average price is currently computed as (_prevPositionSize * _prevAverageEntryPrice + _sizeDelta * _indexPrice)/(prevPositionSize + _sizeDelta), which needs to be revised as (_prevPositionSize + _sizeDelta)/(_prevPositionSize / _prevAverageEntryPrice + _sizeDelta / _indexPrice).
```solidity
function calculateWeightedAverageEntryPrice(
    uint256 _prevAverageEntryPrice,
    uint256 _prevPositionSize,
    int256 _sizeDelta,
    uint256 _indexPrice
) internal pure returns (uint256) {
    if (_sizeDelta <= 0) {
        // If full close, Avg Entry Price is reset to 0
        if (_sizeDelta == -_prevPositionSize.toInt256()) return 0;
        // Else, Avg Entry Price doesn't change for decrease
        else return _prevAverageEntryPrice;
    }
    // Increasing position size
    uint256 newPositionSize = _prevPositionSize + _sizeDelta.abs();
    uint256 numerator = (_prevAverageEntryPrice * _prevPositionSize) + (_indexPrice * _sizeDelta.abs());
    uint256 newAverageEntryPrice = numerator / newPositionSize;
    return newAverageEntryPrice;
}
```

## Recommendation
Revise the above routine to properly compute the next average price when a position is increased.
