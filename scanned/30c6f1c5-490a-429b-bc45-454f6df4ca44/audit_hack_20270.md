# [H] 5.2.1 No price scaling in SMAOracle

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** SMAOracle.sol#L82-L96, ChainlinkOracleWrapper.sol#L36-L

**Description:** Theupdate()function of theSMAOraclecontract doesn’t scale thelatestPricealthough ascaleris
set in the constructor. On the other hand, the_latestRoundData()function ofChainlinkOracleWrappercontract
does scale viatoWad().

```
contract SMAOracle is IOracleWrapper {
```
```
constructor(..., uint256 _spotDecimals, ...) {
...
require(_spotDecimals <= MAX_DECIMALS, "SMA: Decimal precision too high");
...
/*`scaler`is always <= 10^18 and >= 1 so this cast is safe */
scaler = int256(10**(MAX_DECIMALS - _spotDecimals));
...
}
function update() internal returns (int256) {
/* query the underlying spot price oracle */
IOracleWrapper spotOracle = IOracleWrapper(oracle);
int256 latestPrice = spotOracle.getPrice();
...
priceObserver.add(latestPrice); // doesn't scale latestPrice
...
}
```
```
contract ChainlinkOracleWrapper is IOracleWrapper {
function getPrice() external view override returns (int256) {
(int256 _price, ) = _latestRoundData();
return _price;
}
function _latestRoundData() internal view returns (int256, uint80) {
(..., int256 price, ..) = AggregatorV2V3Interface(oracle).latestRoundData();
...
return (toWad(price), ...);
}
```
**Recommendation:** ThelatestPricevariable inSMAOraclecontract should be scaled, and thetoWad()function
should be re-introduced.

Note: If theSMAOracleis only used with WAD based spot oracles, then_spotDecimals == 18must be enforced.

**Tracer:** We are submitting PR 406 as a mitigation for this. It is a slightly larger PR than we originally intended so
as a result it will likely be submitted for several defects here. We would appreciate if each defect could be assessed
against it.

**Spearbit:** Acknowledged.
