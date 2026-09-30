# [M] `externalSwap()` need slippage control

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177
Type: audit-issue

## Details
# `externalSwap()` need slippage control

## Summary

There is no slippage control in `externalSwap()`. Users could lose fund due to high slippage.


## Vulnerability Detail

`externalSwap()` only checks for whitelist contracts, but not slippage. Currently it might assume that slippage is included in `callDataConcat`. But there is no guarantee that proper parameters is in ``callDataConcat`, and no sanity check for it. And the dependence on external protocols might be error prone. 


## Impact

Users could lose fund due to high slippage.


## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L177


## Tool used

Manual Review

## Recommendation

Add the following check for slippage, just like in `mixSwap()` and `dodoMutliSwap()`:
```solidity
    require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");
```
