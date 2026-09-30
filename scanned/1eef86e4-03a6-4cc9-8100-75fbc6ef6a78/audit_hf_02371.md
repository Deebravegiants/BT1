# [M] Revisited _getUniswapV3Price() Logic in Oracle

## Summary
Severity: Medium
Contest weight: 0.4553
Dataset id: 12811
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a core Oracle contract that provides a reliable approach to query the prices of supported assets. While examining the UniswapV3-based price support, we notice it is incorrectly implemented. In the following, we show the related implementation in the _getUniswapV3Price(). This routine has two issues. The first one is the lack of differentiation of two different feed types FeedType.UNI_V30 and FeedType.UNI_V31 in the final token price calculation. In particular, while indexToken and stableToken are properly identified, the related baseUnit should be computed based on indexToken, not stableToken. Also, the second issue is that the current price is only applicable for the FeedType.UNI_V30 case, not FeedType.UNI_V31.
```solidity
function _getUniswapV3Price(IPriceFeed.SecondaryStrategy memory _strategy) private view returns (uint256 price) {
    if (_strategy.feedType != IPriceFeed.FeedType.UNI_V30 && _strategy.feedType != IPriceFeed.FeedType.UNI_V31) {
        revert Oracle_InvalidReferenceQuery();
    }
    IUniswapV3Pool pool = IUniswapV3Pool(_strategy.feedAddress);
    (uint160 sqrtPriceX96,,,,,,) = pool.slot0();
    address indexToken;
    address stableToken;
    if (_strategy.feedType == IPriceFeed.FeedType.UNI_V30) {
        indexToken = pool.token0();
        stableToken = pool.token1();
    } else {
        indexToken = pool.token1();
        stableToken = pool.token0();
    }
    (bool successStable, uint256 stablecoinDecimals) = _tryGetAssetDecimals(IERC20(stableToken));
    if (!successStable) revert Oracle_InvalidAmmDecimals();
    uint256 baseUnit = 10 ** stablecoinDecimals;
    UD60x18 numerator = ud(uint256(sqrtPriceX96)).powu(2).mul(ud(baseUnit));
    UD60x18 denominator = ud(2).powu(192);
    // Scale and return the price to 30 decimal places
    price = unwrap(numerator.div(denominator)) * (10 ** (PRICE_DECIMALS - stablecoinDecimals));
}
```

## Recommendation
Improve the above-mentioned routine to properly compute the UniswapV3-based price
