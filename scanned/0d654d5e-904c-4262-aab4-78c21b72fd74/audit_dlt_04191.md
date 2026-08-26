# [H] DODORouteProxy.sol : The `receiveAmount` from all the swap is not the actual value. It is deducted from all the fee.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/80
Type: sherlock-finding

## Details
ak1

high

# DODORouteProxy.sol : The `receiveAmount` from all the swap is not the actual value. It is deducted from all the fee.

## Summary
During the swap operations, `externalSwap` or `` or `mixSwap` or `dodoMutliSwap`. the `receiveAmount` is returned and the same is emitted.
But the emitted/returned amount value is incorrect as it undergone for fee deduction.

## Vulnerability Detail
When look at the `external swap`
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L174

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L228

Inside the `_routeWithdraw` function, the fee are deducted and remaining value is sent to msg.sender.
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L465-L492

The value that is sent to user and emitted or returned from swap functions are not same.

## Impact
The information about the `receiveAmount` is not correct.
User could be given with incorrect data.

## Code Snippet
For external swap.
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L174
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L228
Similarly we can see for other swaps also.

## Tool used

Manual Review

## Recommendation
return the `receiveAmount` value from `_routeWithdraw` where it has undergone for all type of fee deduction. and use this value to emit and return in all the swaps.
