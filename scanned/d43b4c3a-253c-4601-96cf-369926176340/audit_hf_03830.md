# [M] Chainlink price feed is deprecated, not suffi-

## Summary
Severity: Medium
Contest weight: 0.5867
Dataset id: 20063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function _createActionInfo() uses Chainlink's deprecated latestAnswer function, this function also does not guarantee that the price returned by the Chainlink price feed is not stale and there is no additional checks to ensure that the return values are valid.
The internal function _createActionInfo() uses calls strategy.collateralPriceOracle.latestAnswer() and strategy.borrowPriceOracle.latestAnswer() that uses Chainlink's deprecated latestAnswer() to get the latest price. However, there is no check for if the return value is stale data.
```solidity
function _createActionInfo() internal view returns(ActionInfo memory) {
    ActionInfo memory rebalanceInfo;
    // Calculate prices from chainlink. Chainlink returns prices with 8 decimal places, but we need 36 - underlyingDecimals decimal places.
    // This is so that when the underlying amount is multiplied by the received price, the collateral valuation is normalized to 36 decimals.
    // To perform this adjustment, we multiply by 10^(36 - 8 - underlyingDecimals)
    int256 rawCollateralPrice = strategy.collateralPriceOracle.latestAnswer();

    rebalanceInfo.collateralPrice = rawCollateralPrice.toUint256().mul(10 ** strategy.collateralDecimalAdjustment);

    int256 rawBorrowPrice = strategy.borrowPriceOracle.latestAnswer();
    rebalanceInfo.borrowPrice = rawBorrowPrice.toUint256().mul(10 ** strategy.borrowDecimalAdjustment);

    // More Code....
}
```
The function _createActionInfo() is used to return important values used throughout the contract, the staleness of the chainlink return values will lead to wrong calculation of the collateral and borrow prices and other unexpected behavior.

## Recommendation
The latestRoundData function should be used instead of the deprecated latestAnswer function and add sufficient checks to ensure that the pricefeed is not stale.
```solidity
(uint80 roundId, int256 assetChainlinkPriceInt, , uint256 updatedAt, uint80 answeredInRound) = IPrice(_chainlinkFeed).latestRoundData();

require(answeredInRound >= roundId, "price is stale");
require(updatedAt > 0, "round is incomplete");
```
