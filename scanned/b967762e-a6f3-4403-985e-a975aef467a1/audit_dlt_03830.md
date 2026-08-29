# [M] Price can be miscalculated.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-olympus
Published: 2023-12-26
Source: https://github.com/sherlock-audit/2023-11-olympus-judging/issues/56
Type: sherlock-finding

## Details
dany.armstrong90

medium

# Price can be miscalculated.

## Summary
In `SimplePriceFeedStrategy.sol#getMedianPrice` function, when the length of `nonZeroPrices` is 2 and they are deviated it returns first non-zero value, not median value.

## Vulnerability Detail
`SimplePriceFeedStrategy.sol#getMedianPriceIfDeviation` is as follows.
```solidity
    function getMedianPriceIfDeviation(
        uint256[] memory prices_,
        bytes memory params_
    ) public pure returns (uint256) {
        // Misconfiguration
        if (prices_.length < 3) revert SimpleStrategy_PriceCountInvalid(prices_.length, 3);

237     uint256[] memory nonZeroPrices = _getNonZeroArray(prices_);

        // Return 0 if all prices are 0
        if (nonZeroPrices.length == 0) return 0;

        // Cache first non-zero price since the array is sorted in place
        uint256 firstNonZeroPrice = nonZeroPrices[0];

        // If there are not enough non-zero prices to calculate a median, return the first non-zero price
246     if (nonZeroPrices.length < 3) return firstNonZeroPrice;

        uint256[] memory sortedPrices = nonZeroPrices.sort();

        // Get the average and median and abort if there's a problem
        // The following two values are guaranteed to not be 0 since sortedPrices only contains non-zero values and has a length of 3+
        uint256 averagePrice = _getAveragePrice(sortedPrices);
253     uint256 medianPrice = _getMedianPrice(sortedPrices);

        if (params_.length != DEVIATION_PARAMS_LENGTH) revert SimpleStrategy_ParamsInvalid(params_);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-11-olympus-judging/issues/56_
