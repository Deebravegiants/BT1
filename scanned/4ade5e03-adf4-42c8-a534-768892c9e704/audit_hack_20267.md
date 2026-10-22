# [M] 3.3.7 Error codes ofQuotefunctions are unchecked

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** LSSVMPair.sol#L389-431,LSSVMRouter.sol

**Description:** The error return values from functions getBuyNFTQuote() and
getSellNFTQuote()are not checked in contractLSSVMRouter.sol, whereas other
functions in contractLSSVMPair.soldo check forerror==CurveErrorCodes.Err
or.OK.

```
abstract contract LSSVMPair is Ownable, ReentrancyGuard {
...
function getBuyNFTQuote(uint256 numNFTs) external view returns
,! (CurveErrorCodes.Error error, ...) {
(error, ...) = bondingCurve().getBuyInfo(...);
}
function getSellNFTQuote(uint256 numNFTs) external view returns
,! (CurveErrorCodes.Error error, ...) {
(error, ...) = bondingCurve().getSellInfo(...);
}
function swapTokenForAnyNFTs(...) external payable virtual returns
,! (uint256 inputAmount) {
...
(error, ...) = _bondingCurve.getBuyInfo(...);
require(error == CurveErrorCodes.Error.OK, "Bonding curve error");
...
}
}
```
LSSVMRouter.sol#L

```
(, , pairOutput, ) = swapList[i].pair.getSellNFTQuote(...);
```
The following contract lines contain the same code snippet below:LSSVMRoute
r.sol#L360, LSSVMRouter.sol#L407, LSSVMRouter.sol#L450, LSSVMRouter.so
l#L493,LSSVMRouter.sol#L627,LSSVMRouter.sol#L

```
(, , pairCost, ) = swapList[i].pair.getBuyNFTQuote(...);
```
**Note:** The current Curve contracts, which implement the getBuyNFTQuote()
and getSellNFTQuote()functions, have a limited number of potential errors.
However, future Curve contracts might add additional error codes.

**Recommendation:** Check the error code of functionsgetBuyNFTQuote()and
getSellNFTQuote()in contractLSSVMRouter.sol.


**Sudoswap:** Addressed in this branch here. LSSVMRouter now reverts if the
Error is notError.OKfor a normal swap, or it skips performing the swap during
a robust swap operation.

**Spearbit:** Acknowledged.
