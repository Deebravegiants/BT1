# [M] Improved getNextAveragePrice() Logic in Vault

## Summary
Severity: Medium
Contest weight: 0.4259
Dataset id: 12410
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LionDEX protocol has a key Vault contract that allows the user to create or adjust his/her trading positions. While examining the current position-related logic, we notice the price adjustment of an increased position can be improved. To elaborate, we show below the implementation of the getNextAveragePrice() routine. As the name indicates, this routine computes the next average price when a position is increased with _sizeDelta (line 964). Speciﬁcally, for current position of _size with its _averagePrice, if it is increased by _sizeDelta with the latest mark price _nextPrice, the next average price is currently computed as (_size * _averagePrice + _sizeDelta * _nextPrice)/(_size + _sizeDelta), which needs to be revised as (_size + _sizeDelta)/(_size / _averagePrice + _sizeDelta / _nextPrice).
```solidity
function getNextAveragePrice(
    address _indexToken,
    uint256 _size,
    uint256 _averagePrice,
    uint256 _nextPrice, // index token price current
    uint256 _sizeDelta
) public view returns (uint256) {
    require(
        whitelistedTokens[_indexToken],
        "Vault: getNextAveragePrice index token not white listed"
    );
    if (_size == 0) {
        return _nextPrice;
    }
    return _size.mul(_averagePrice).add(_sizeDelta.mul(_nextPrice)).div(
        _size.add(_sizeDelta)
    );
}
```

## Recommendation
Revise the above routine to properly compute the next average price when a position is increased.
