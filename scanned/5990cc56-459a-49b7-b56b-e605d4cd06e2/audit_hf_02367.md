# [M] Incorrect ADL Impact Calculation Logic in Execution

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 12803
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a core Execution contract that is designed to execute user orders and update user positions. A specific order is named ADL, which aims to automatically de-leverage the user position if the position's profit reaches the protocol-specified threshold. The ADL execution needs to adjust the execution price for the affected positions within specific boundaries to maintain market health. Our analysis shows the current approach to calculate the execution price is incorrect. In the following, we show the implementation of the related routine, i.e., _executeAdlImpact(). We notice the use of percentage() to calculate acceleration factor accelerationFactor (line 751), which should be revised as below: accelerationFactor = (_pnlToPoolRatio - TARGET_PNL_FACTOR).percentage(PRECISION, TARGET_PNL_FACTOR). Similarly, the pool impact needs to be corrected as pnlImpact = pnlImpact.percentage(PRECISION, _poolUsd) (line 755).
```solidity
function _executeAdlImpact(
    uint256 _indexPrice,
    uint256 _averageEntryPrice,
    uint256 _pnlBeingRealized,
    uint256 _poolUsd,
    uint256 _pnlToPoolRatio,
    bool _isLong
) private pure returns (uint256 impactedPrice) {
    uint256 accelerationFactor = (_pnlToPoolRatio - TARGET_PNL_FACTOR).percentage(TARGET_PNL_FACTOR);
    uint256 pnlImpact = _pnlBeingRealized * accelerationFactor / PRECISION;
    uint256 poolImpact = pnlImpact.percentage(_poolUsd);
    if (poolImpact > PRECISION) poolImpact = PRECISION;
    // Calculate the minimum profit price for the position, where profit = 5% of position (average entry price +- 5%)
    uint256 minProfitPrice = _isLong
        ? _averageEntryPrice + (_averageEntryPrice.percentage(MIN_PROFIT_PERCENTAGE))
        : _averageEntryPrice - (_averageEntryPrice.percentage(MIN_PROFIT_PERCENTAGE));
    uint256 priceDelta = (_indexPrice.absDiff(minProfitPrice) * poolImpact) / PRECISION;
    if (_isLong) impactedPrice = _indexPrice - priceDelta;
    else impactedPrice = _indexPrice + priceDelta;
}
```

## Recommendation
Improve the above-mentioned routine to properly adjust the execution price for an ADL order.
