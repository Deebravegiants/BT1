# [M] Incorrect FundingRate And Velocity Update in Funding

## Summary
Severity: Medium
Contest weight: 0.4172
Dataset id: 12810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a Funding library contract that is designed to facilitate the funding-related calculations. In the process of examining current update logic of funding rates, we notice its implementation has a flaw that needs to be fixed. In the following, we show the implementation of the affected routine updateState(). It has a rather straightforward logic in updating the given pool's fundingRate, fundingAccruedUsd, and fundingRateVelocity. Note the fundingRateVelocity update should come after the fundingRate update. However, current implementation incorrectly updates fundingRateVelocity before updating fundingRate.
```solidity
function updateState(
    MarketId _id,
    IMarket market,
    Pool.Storage storage pool,
    string calldata _ticker,
    uint256 _indexPrice,
    int256 _sizeDelta,
    bool _isLong
) internal {
    int256 nextSkew = _calculateNextSkew(_id, market, _ticker, _sizeDelta, _isLong);
    pool.fundingRateVelocity = getCurrentVelocity(market, nextSkew, pool.config.maxFundingVelocity, pool.config.skewScale).toInt64();
    (pool.fundingRate, pool.fundingAccruedUsd) = calculateNextFunding(_id, market, _ticker, _indexPrice);
}
```

## Recommendation
Improve the above-mentioned routine to properly update various pool's states.
