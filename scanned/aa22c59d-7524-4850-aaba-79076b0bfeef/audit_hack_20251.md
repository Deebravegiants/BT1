# [M] 5.2.1 Rounding down ofsnapAccumulatormight influence calculations

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Roller.sol#L23-L
**Description:** The functiontransform()lowerssnapAccumulatorwith the following equation:(snapAccumulator
* int256(dt)) / int256(snapWindow). During the time thatsnapAccumulator * dtis smaller thansnapWindow
this will be rounded down to 0 , which meanssnapAccumulatorwill stay at the same value. Luckily,dtwill eventually
reach the value ofsnapWindowand by then the value won’t be rounded down to 0 any more. Risk lies in calculations
diverging from formulas written in the whitepaper.
Note: Given medium risk severity because the probability of this happening is high, while impact is likely low.

```
function transform(...) ... {
snapAccumulator -= (snapAccumulator * int256(dt)) / int256(snapWindow);
}
```
**Recommendation:** Confirm that rounding down does not influence calculations too much.
**Overlay** : Confirmed and agreed. Fixed in commit 9b1865e.
**Spearbit:** Acknowledged.
