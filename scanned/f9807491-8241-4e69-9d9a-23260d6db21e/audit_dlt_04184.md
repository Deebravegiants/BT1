# [M] MODIFIER `judgeExpired` CAN BE BYPASSED

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/95
Type: sherlock-finding

## Details
Mukund

medium

# MODIFIER `judgeExpired` CAN BE BYPASSED

## Summary
Modifier judgeExpired check for deadline parameter which is uint256 and its user controlled a malicious user can pass a random deadline value which passes the check and bypass it.
## Vulnerability Detail

## Impact
use can call function even after its expired
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L91
## Tool used
none
Manual Review

## Recommendation
add proper checks
