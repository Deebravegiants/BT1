# [M] MODIFIER `judgeExpired` CAN BE BYPASSED

## Summary
Severity: Medium
Reporter: Mukund
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L91
Type: audit-issue

## Details
# MODIFIER `judgeExpired` CAN BE BYPASSED

Modifier judgeExpired check for deadline parameter which is uint256 and its user controlled a malicious user can pass a random deadline value which passes the check and bypass it.
User can call function even after its expired.
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L91
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L174
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L250
