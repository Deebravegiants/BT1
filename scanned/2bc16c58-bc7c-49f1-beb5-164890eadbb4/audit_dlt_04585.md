# [H] Missing available balance validation

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/80
Type: sherlock-finding

## Details
silviaxyz

high

# Missing available balance validation

## Summary
If totalLockedAmount is equals or more than totalPoolBalance it cause availableBalance to be wrong.

## Vulnerability Detail
There is no available balance validation on this function.

## Impact
High

## Code Snippet

https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L293


There should be better validation for available balance.
https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L406

## Tool used

Manual Review

## Recommendation
Validate availablebalance.
