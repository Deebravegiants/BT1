# [H] `minReturnAmount` value not checked in the `externalSwap` function.

## Summary
Severity: High
Reporter: jayphbee
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L170
Type: audit-issue

## Details
# `minReturnAmount` value not checked in the `externalSwap` function.

## Summary
The `minReturnAmount` parameter protects user from unexpected slippage, but it's not validated if it's value is greater than 0 or not, which can leads to user suffers from sandwich-attack.

## Vulnerability Detail
User call `externalSwap` function to swap `fromToken` to `toToken` but unexpectedly not set value for `minReturnAmount`. An MEV bot detect this transaction and then perfrom sandwich-attack to it, which leads to user could get far more less `toToken` than expected.

## Impact
User's transaction is sandwich-attacked thus lose funds.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L170

## Tool used

Manual Review

## Recommendation
Check `minReturnAmount` like `mixSwap` and `dodoMutliSwap` do.
```solidity
require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");
```
