# [M] 6.3 Protocol Fee Computation Can Overflow

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The protocol fee computation in loanTerms can overflow if the protocolFee is non-zero. The
multiplication in _protocolFee = uint128((_inAmountAfterFees * protocolFee) / BASE)
is carried in uint128 and might overflow. Example is with protocolFee = 5 * 10**5 which is also
the maximum allowed fee and _inAmountAfterFees=uint128(uint256(2**128) / uint256(
*10**15))+1=68056473384187692692675 which may seem to be a lot but could be a realistic
amount for collateral tokens with 18 decimals and low value.

Code corrected

In the second version of the codebase, the variable protocolFee was renamed creatorFee and its
type was changed to uint256 to avoid possible overflows in the computation highlighted in the issue
above.
