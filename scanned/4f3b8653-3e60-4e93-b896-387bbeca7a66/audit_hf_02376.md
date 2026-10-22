# [M] Unsound PriceCalculator Assumption On Asset Decimals

## Summary
Severity: Medium
Contest weight: 0.4539
Dataset id: 12831
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Qubit protocol has an important oracle-related contract named PriceCalculatorBSC. This contract is essential to query for the price of the underlying assets behind supported QTokens. In particular, it has a main function getUnderlyingPrice() that is used to obtain the price of the given asset and has been used in various scenarios, including the calculation of collateralized assets in USD for health check etc.
To elaborate, we show below the related getUnderlyingPrice() function. It implements a rather straightforward logic in firstly querying the effective price feed, then checking the valid hardcoded price, and finally converting the resulting amount with the BNB denomination. However, it comes to our attention that the computation makes an implicit assumption of the asset decimal, i.e., 18. Unfortunately, this assumption may not always hold! When violated, it may be of serious detriment to the overall protocol operations, including the collateralization evaluation and allowed borrow amount calculation.
```solidity
function priceOf(address asset) public view override returns (uint priceInUSD) {
    (, priceInUSD) = _oracleValueOf(asset, 1e18);
    return priceInUSD;
}
function getUnderlyingPrice(address qToken) public view override returns (uint) {
    return priceOf(IQToken(qToken).underlying());
}
function _oracleValueOf(address asset, uint amount) private view returns (uint valueInBNB, uint valueInUSD) {
    valueInUSD = 0;
    if (tokenFeeds[asset] != address(0)) {
        (, int price, , , ) = AggregatorV3Interface(tokenFeeds[asset]).latestRoundData();
        valueInUSD = uint(price).mul(1e10).mul(amount).div(1e18);
    } else if (references[asset].lastUpdated > block.timestamp.sub(1 days)) {
        valueInUSD = references[asset].lastData.mul(amount).div(1e18);
        valueInBNB = valueInUSD.mul(1e18).div(priceOfBNB());
    }
}
```

## Recommendation
Revise the above getUnderlyingPrice() routine to properly take into account the asset decimal.
