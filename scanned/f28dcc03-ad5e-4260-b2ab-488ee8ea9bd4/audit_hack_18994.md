# [M] missing emit events in `setPaused` function

## Summary
Severity: Medium
Reporter: Restless Mulberry Manatee
Source: https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L110-L116
Type: audit-issue

## Details
# missing emit events in `setPaused` function

krkba
## Summary

## Vulnerability Detail
Setter-functions must emit events
## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L110-L116
## Tool used

Manual Review

## Recommendation
Emit events in setter functions
