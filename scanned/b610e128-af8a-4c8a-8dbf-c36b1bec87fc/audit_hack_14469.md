# [M] Auction can begin in the past

## Summary
Severity: Medium
Reporter: rvdemonk
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Auction can begin in the past

## Summary

Auction can begin in the past.

## Vulnerability Detail

No check in the constructor ensuring that startTime is not in the past.

## Impact

Potentially unintended functionality.

## Code Snippet

## Tool used

Manual Review

## Recommendation

Require that startTime >= block.timestamp.
