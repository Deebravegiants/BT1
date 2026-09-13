# [M] Missing validation in `sendMessage` function

## Summary
Severity: Medium
Reporter: Restless Mulberry Manatee
Source: https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L300-L321
Type: audit-issue

## Details
# Missing validation in `sendMessage` function

krkba
## Summary

## Vulnerability Detail
The `recipient` is not validated in `sendMessage` function.
## Impact
It's possible to send a message to an empty address.
## Code Snippet
https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L300-L321
## Tool used

Manual Review

## Recommendation
Add check for `recipient`.
