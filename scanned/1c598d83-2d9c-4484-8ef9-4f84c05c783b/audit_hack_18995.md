# [H] Missing input validation in `mint` and `burn` function

## Summary
Severity: High
Reporter: Restless Mulberry Manatee
Source: https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/WrappedAvail.sol#L30-L37
Type: audit-issue

## Details
# Missing input validation in `mint` and `burn` function

krkba
## Summary

## Vulnerability Detail
There is no input validation in `mint` and `burn` function.
## Impact
It's possible to burn more tokens than a user has or mint an excessively large number of tokens.
## Code Snippet
https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/WrappedAvail.sol#L30-L37
## Tool used

Manual Review

## Recommendation
Add checks to prevent these scenarios.
