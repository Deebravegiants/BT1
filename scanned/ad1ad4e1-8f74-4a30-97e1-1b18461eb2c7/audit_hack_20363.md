# [M] 5.2.1 getSpotPrice,approximateReservesGivenPrice,getStrategyDataignore time to maturity

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** NormalStrategyLib.sol#L

**Description:** When callinggetSpotPrice,getStrategyDataorapproximateReservesGivenPrice, the pool con-
fig istransformed into aNormalCurvestruct. This transformation always sets the time to maturity field to the entire
duration


```
function transform(PortfolioConfig memory config)
pure
returns (NormalCurve memory)
{
return NormalCurve({
reserveXPerWad: 0,
reserveYPerWad: 0,
strikePriceWad: config.strikePriceWad,
standardDeviationWad: config.volatilityBasisPoints.bpsToPercentWad(),
timeRemainingSeconds: config.durationSeconds,
invariant: 0
});
}
```
Neither is thecurve.timeRemainingSecondsvalue overridden with the correct value for the mentioned functions.
The reported spot price will be wrong after the pool has been initialized and integrators cannot rely on this value.

**Recommendation:** Initialize thetimeRemainingSecondsvalue intransformto the current time remainings value
or set it to the correct value afterwards for functions where it is needed. It should use a value similar to what
computeTau(..., block.timestamp)returns. Consider adding additional tests for the affected functions for pools
that have been active for a while.

**Primitive:** Fixed in commit 15ee0f.

**Spearbit:** Fixed. It was changed forgetSpotPrice, comments have been added to the other functions.
