# [M] DODORouteProxy.sol#L170: Lack of slippage protection for `externalSwap`

## Summary
Severity: Medium
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L254
Type: audit-issue

## Details
# DODORouteProxy.sol#L170: Lack of slippage protection for `externalSwap`

## Summary
When calling the `externalSwap` function, `minReturnAmount` is used to protect from unfair slippage events.
But there is no validation whether the `minReturnAmount > 0`. 

I am raising this as issue by looking at other places where this validation is done.

for `mixswap`, the check is done here, https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L254

for `dodoMutliSwap`, the check is done here, https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L339


## Vulnerability Detail

For `externalSwap`, there is no check whether the `minReturnAmount` value is greater than zero or not.

but , other type swaps has this validation. Refer the summary section for code reference where other functions has this check.

## Impact
There will not be any protection from slippage if the `minReturnAmount` is not validated.

The check from `routewithdraw` will not catch this flaw.

        require(receiveAmount >= minReturnAmount, "DODORouteProxy: Return amount is not enough");

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L179

## Tool used

Manual Review

## Recommendation

Check whether the `minReturnAmount > 0` inside the `externalSwap` function.

or

Add this check inside the `_routeWithdraw` function so that all other swaps will be covered.
