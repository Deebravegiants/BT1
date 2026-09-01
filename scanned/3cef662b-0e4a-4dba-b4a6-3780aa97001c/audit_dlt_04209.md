# [M] Owner can set `routeFeeRate` to 99.99%

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/49
Type: sherlock-finding

## Details
pashov

medium

# Owner can set `routeFeeRate` to 99.99%

## Summary
There is centralisation risk from the owner being able to set a very high route fee rate

## Vulnerability Detail
The `changeRouteFeeRate()` method in `DODORouteProxy.sol` is checking if the fee is less than 100%, but it can be set to 99.999%. If this is the case and a user is using 0 slippage protection he will lose all of his funds to the protocol. This can also be done as a sandwich attack from a malicious/compromised owner.

## Impact
The impact is potential loss for users, but happens in a special scenario hence Medium severity.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L130

## Tool used

Manual Review

## Recommendation
Add a `MAX_ROUTE_FEE_RATE` constant with a sensible value, for example 10%, and check that the new feeRate is below it
