# [M] Use `safeTransfer()` instead of `transfer()` for ERC20 transfers

## Summary
Severity: Medium
Reporter: sach1r0
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L420
Type: audit-issue

## Details
# Use `safeTransfer()` instead of `transfer()` for ERC20 transfers

## Summary
`_multiSwap` function uses the `transfer()` method instead of `safeTransfer()`.

## Vulnerability Detail
Some ERC20 tokens that are not compliant with the specification could return false from the transfer function call to indicate that the transfer fails, but the calling contract would not notice the failure if the return value is not checked.The EIP-20 specification requires to check the return value.
See reference for similar issue: https://github.com/code-423n4/2021-08-yield-findings/issues/36

## Impact
Callers might not properly handle tokens that are not ERC20 compliant.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L420
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L423

## Tool used
Vim and Manual Review

## Recommendation
I recommend using the `safeTransfer()` method by OpenZeppelin instead of `transfer()`.
