# [H] The price of `squeethEthPrice` obtained by `_calcFeeAdjustment()` is inconsistent with other prices

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/174
Type: sherlock-finding

## Details
8olidity

high

# The price of `squeethEthPrice` obtained by `_calcFeeAdjustment()` is inconsistent with other prices

## Summary
The price of `squeethEthPrice` obtained by `_calcFeeAdjustment()` is inconsistent with other prices
## Vulnerability Detail
In the `_calcFeeAdjustment()` function, the code uses the following method to obtain the price

```solidity
uint256 squeethEthPrice = IOracle(oracle).getTwap(ethSqueethPool, sqth, weth, sqthTwapPeriod, true);
```
The parameter passed here is `sqthTwapPeriod` is `420 seconds`. But other functions get `squeethEthPrice` as follows
```solidity
uint256 squeethEthPrice = IOracle(oracle).getTwap(ethSqueethPool, sqth, weth, auctionTwapPeriod, true);
```
But the value of `auctionTwapPeriod` can be changed
```solidity
    function setAuctionTwapPeriod(uint32 _auctionTwapPeriod) external onlyOwner {
        require(_auctionTwapPeriod >= 180, "twap period cannot be less than 180");
        uint32 previousTwap = auctionTwapPeriod;

        auctionTwapPeriod = _auctionTwapPeriod;

        emit SetAuctionTwapPeriod(previousTwap, _auctionTwapPeriod);
    }
```
If the administrator modifies the value of `auctionTwapPeriod`, the price obtained by `_calcFeeAdjustment` will be different from the price calculated by other functions in the contract.

For example in `depositAuction()`, first check the price with `_checkOTCPrice`. Here is the calculation using `auctionTwapPeriod`

```solidity
function _checkOTCPrice(uint256 _price, bool _isAuctionBuying) internal view {
        // Get twap
        uint256 squeethEthPrice = IOracle(oracle).getTwap(ethSqueethPool, sqth, weth, auctionTwapPeriod, true);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/174_
