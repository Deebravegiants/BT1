# [M] PricerInternal.sol#L62 : The function could revert when subtracting the uint256 number from unint64

## Summary
Severity: Medium
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L62-L68
Type: audit-issue

## Details
# PricerInternal.sol#L62 : The function could revert when subtracting the uint256 number from unint64

## Summary
PricerInternal.sol#L62 : The function could revert when subtracting the  unint256 from uint64
Typecasting for uint256 is missed to convert it a uint64.

## Vulnerability Detail
The function `_getTimeToMaturity64x64` returns time remaining until maturity
when we look at the line 67, `return ABDKMath64x64.divu(expiry - block.timestamp, 365 days);`
`expiry is uint 64` whereas `block.timestamp is uint 256`

When we subtract the uint256 from uint64, often overflow happens and the function could revert.


## Impact

The function could revert and can not behave correctly.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L62-L68

## Tool used

Manual Review

## Recommendation
`return ABDKMath64x64.divu(expiry - block.timestamp, 365 days);`
in above line of code, typecast the `block.timestamp` to `uint64`
