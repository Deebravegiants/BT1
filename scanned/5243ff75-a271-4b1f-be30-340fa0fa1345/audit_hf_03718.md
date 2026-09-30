# [M] Negative prices will cause old orders to be

## Summary
Severity: Medium
Contest weight: 0.5706
Dataset id: 19836
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In most cases where orders are submitted using invalid oracle prices, the check for
isEmptyPriceError() returns true, and the order execution is allowed to revert,
rather than canceling the order.
Negative Chainlink oracle prices (think negative interest rates in Europe) result in a
plain revert(<string>), which isn't counted as one of these errors, and so if the
price becomes negative, any outstanding order will be canceled, even if the order
was submitted prior to the price going negative.
Orders to close positions will be canceled, leading to losses.
Chainlink prices are converted to positive numbers:
```solidity
// File: gmx-synthetics/contracts/oracle/Oracle.sol :
Oracle._setPricesFromPriceFeeds()
    (
        /* uint80 roundID */,
        int256 _price,
        /* uint256 startedAt */,
        /* uint256 timestamp */,
        /* uint80 answeredInRound */
    ) = priceFeed.latestRoundData();
    uint256 price = SafeCast.toUint256(_price);
```
And if they're negative, the code reverts:
```solidity
// File: gmx-synthetics/node_modules/@openzeppelin/contracts/utils/math/SafeCast.sol
// : SafeCast.toUint256()
    function toUint256(int256 value) internal pure returns (uint256) {
        require(value >= 0, "SafeCast: value must be positive");
        return uint256(value);
    }
```
Orders that revert get frozen or canceled

## Recommendation
Create a new error type, and include it in the list of
OracleUtils.isEmptyPriceError() errors
