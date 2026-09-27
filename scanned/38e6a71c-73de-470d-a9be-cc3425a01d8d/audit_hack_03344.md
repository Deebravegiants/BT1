# [M] _routeWithdraw() function has call to sender without reentrancy protection

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L488
Type: audit-issue

## Details
# _routeWithdraw() function has call to sender without reentrancy protection

## Summary

## Vulnerability Detail

## Impact
This allows the caller to reenter this and other functions in this and other protocol files. To prevent reentrancy and cross function reentrancy there should be reentrancy guard modifiers placed on the _routeWithdraw() function and any other function that makes external calls to the caller.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L488

        'IWETH(_WETH_).withdraw(receiveAmount);'

## Tool used

Manual Review

## Recommendation
Add reentrancy guard modifier to _routeWithdraw() function.
