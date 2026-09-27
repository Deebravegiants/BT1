# [H] 6.8 Calling _liquidityDelta Incorrectly

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function postPreOrder in Lstrategy calls _liquidityDelta as follows:

```
(uint256 tokenDelta, bool isNegative) = _liquidityDelta(
tvl[0],
tvl[0] + tvl[1],
ratioParams.erc20TokenRatioD,
ratioParams.minErc20TokenRatioDeviationD
);
```
As already pointed out in the issue Calling _liquidityDelta with incorrect inputs, the function
_liquidityDelta also performs the addition, hence computing incorrectly the result.

Code corrected:

The parameters passed to the function _liquidityDelta have been corrected, namely the addition of
tvl[0] + tvl[1] is removed and only tvl[1] is passed as the second argument of the function call.
