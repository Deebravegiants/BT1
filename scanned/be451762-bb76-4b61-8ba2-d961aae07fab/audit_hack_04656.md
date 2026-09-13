# [H] Insufficient mapping to approve multiple whitelistedAssets

## Summary
Severity: High
Reporter: dinesh
Source: https://github.com/sherlock-audit/2023-01-uxd/blob/main/contracts/core/UXDControllerStorage.sol#L20
Type: audit-issue

## Details
# Insufficient mapping to approve multiple whitelistedAssets

## Summary
Insufficient mapping to approve multiple whitelistedAssets

## Vulnerability Detail
At https://github.com/sherlock-audit/2023-01-uxd/blob/main/contracts/core/UXDControllerStorage.sol#L20

    mapping(address => bool) public whitelistedAssets;

## Impact
This implementation doesn’t support multi-whitelistedAssets

## Code Snippet

## Tool used

Manual Review

## Recommendation
mapping(address =>mapping(address => bool) public whitelistedAssets;
