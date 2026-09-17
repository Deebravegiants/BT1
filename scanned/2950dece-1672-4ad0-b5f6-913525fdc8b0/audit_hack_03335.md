# [M] DODORouteProxy._routeWithdraw uses transfer to send eth

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L489
Type: audit-issue

## Details
# DODORouteProxy._routeWithdraw uses transfer to send eth

## Summary
DODORouteProxy._routeWithdraw uses transfer to send eth which only provides 2300 gas. This can be not enough for some contracts.
## Vulnerability Detail
DODORouteProxy can be used not only by EOA, but also by contracts. For some of them it can be not enough 2300 gas in receive function, so they  will not be able to use the protocol, because of that.
## Impact
Some contracts can't use protocol
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L489
## Tool used

Manual Review

## Recommendation
Use call instead of transfer.
