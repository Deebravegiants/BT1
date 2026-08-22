# [M] Function `convertToUnderlying(uint256 s)` does not follow EIP5095

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/182
Type: sherlock-finding

## Details
JohnSmith

medium

# Function `convertToUnderlying(uint256 s)` does not follow EIP5095

## Summary
The `convertToUnderlying` function does not follow EIP5095 standard, when called before maturity
## Vulnerability Detail
according to https://eips.ethereum.org/EIPS/eip-5095
`convertToUnderlying`
> Before maturity, the amount of underlying returned is as if the PTs would be at maturity.

in illuminate docs  stateв that
> upon maturity, may redeem the underlying at a 1:1 ratio

when `block.timestamp < maturity` we call `previewRedeem(s)`
```solidity
src/tokens/ERC5095.sol
64:         if (block.timestamp < maturity) {
65:             return previewRedeem(s);
66:         }
```
which will lead to `IYield(pool).buyBasePreview(Cast.u128(a));`
Such implementation will result in not having 1:1

## Impact
Users, who view this as implementation of EIP5095 will get not expected results, which may lead to some value loss.
## Code Snippet
https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L64-L66
## Tool used

Manual Review

## Recommendation
Always return promised 1:1
```diff
src/tokens/ERC5095.sol
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/182_
