# [M] 5.3.8 pairFordoes not correctly sort tokens when overriding forSinkConverter

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Router.sol#L59-L90
**Description:** The router will always search for pairs by sorting tokenA and TokenB.
Notably, for the velo and Velo2 pair, the Router will not perform the sorting


```
//Router.sol#L69-L73
if (factory == defaultFactory) {
if ((tokenA == IPairFactory(defaultFactory).velo()) && (tokenB ==
,! IPairFactory(defaultFactory).veloV2())) {
return IPairFactory(defaultFactory).sinkConverter();
}
}
```
Meaning that the pair for Velo -> Velo2 will be the Sink but the pair for Velo2 -> Velo will be some other pair.
Additionally, you can front-run a call to setSinkConverter() by calling createPair() with the same parameters. How-
ever, the respective values for getPair() would be overwritten with the sinkConverter address. This could lead to
some weird and unexpected behaviour as we would still have an invalid Pair contract for the v1 and v2 velo tokens.
**Recommendation:** It may be best to enforce the 1 way direction but sort the pair to ensure that all Velo -> Velo2
go to the Sink.
**Velodrome:** Fix implemented commit b0adb4. The front-run still exists where a legitVELO/VELO V2token pair
could be created but from the router perspective, oncePairFactory.setSinkConverter()is called, the invalid
created pair would be ignored.
**Spearbit:** Verified.
