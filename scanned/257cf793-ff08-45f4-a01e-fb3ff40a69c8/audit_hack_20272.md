# [H] 5.2.4 InitialexecutionPriceis too high

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** PoolKeeper.sol#L

**Description:** When a pool is deployed the initialexecutionPriceis calculated asfirstPrice * 1e18where
firstPriceisILeveragedPool(_poolAddress).getOraclePrice():

```
contract PoolKeeper is IPoolKeeper, Ownable {
function newPool(address _poolAddress) external override onlyFactory {
int256 firstPrice = ILeveragedPool(_poolAddress).getOraclePrice();
int256 startingPrice = ABDKMathQuad.toInt(ABDKMathQuad.mul(ABDKMathQuad.fromInt(firstPrice),
,! FIXED_POINT));
executionPrice[_poolAddress] = startingPrice;
}
}
```
All other updates toexecutionPriceuse the result ofgetPriceAndMetadata()directly without scaling:

```
function performUpkeepSinglePool() {
...
(int256 latestPrice, ...) = pool.getUpkeepInformation();
...
executionPrice[_pool] = latestPrice;
...
}
```
```
contract LeveragedPool is ILeveragedPool, Initializable, IPausable {
function getUpkeepInformation() {
(int256 _latestPrice, ...) = IOracleWrapper(oracleWrapper).getPriceAndMetadata();
return (_latestPrice, ...);
}
}
```
The price after thefirstPricewill always be lower, therefore its funding rate payment will always go to the shorts
and long pool token holders will incur a loss.

**Recommendation:** The1e18scaling should be removed for the initialexecutionPrice

- int256 startingPrice = ABDKMathQuad.toInt(ABDKMathQuad.mul(ABDKMathQuad.fromInt(firstPrice),
    ,! FIXED_POINT));
+ int256 startingPrice = firstPrice;

**Tracer:** Valid. Fixed in commit 445377f.

**Spearbit:** Acknowledged.
