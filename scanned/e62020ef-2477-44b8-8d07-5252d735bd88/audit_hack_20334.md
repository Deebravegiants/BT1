# [H] 5.1.8 Error return codes ofgetBuyInfo()andgetSellInfo()are sometimes ignored

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** ICurve.sol#L38-L87, LSSVMPair.sol#L206-L

**Description:** The functionsgetBuyInfo()andgetSellInfo()return an error code when they detect an error.
The rest of the returned parameters then have an unusable/invalid value (0). However, some callers of these
functions ignore the error code and continue processing with the other unusable/invalid values. The functions
getBuyNFTQuote(),getSellNFTQuote()andgetSellNFTQuoteWithRoyalties()pass through the error code, so
their callers have to check the error codes too.


```
function getBuyInfo(...) ... returns (CurveErrorCodes.Error error, ... ) {
}
function getSellInfo(...) ... returns (CurveErrorCodes.Error error, ... ) {
}
function getBuyNFTQuote(...) ... returns (CurveErrorCodes.Error error, ... ) {
(error, ... ) = bondingCurve().getBuyInfo(...);
}
function getSellNFTQuote(...) ... returns (CurveErrorCodes.Error error, ... ) {
(error, ... ) = bondingCurve().getSellInfo(...);
}
function getSellNFTQuoteWithRoyalties(...) ... returns (CurveErrorCodes.Error error, ... ) {
(error, ... ) = bondingCurve().getSellInfo(...);
}
```
**Recommendation:** Always check the return code of the functionsgetBuyInfo(),getSellInfo(),getBuyN-
FTQuote(),getSellNFTQuote()andgetSellNFTQuoteWithRoyalties().

**Sudorandom Labs:** Solved in PR#94.

**Spearbit:** Verified that this is fixed by PR#94.
