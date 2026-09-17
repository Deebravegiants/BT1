# [M] ERC20 transfer should check return value

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L171
Type: audit-issue

## Details
# ERC20 transfer should check return value

## Summary

ERC20 transfer should check return value, otherwise, the token transfer succeeds by default, damage to the protocol.

## Vulnerability Detail

ERC20 tokens only stipulate that the transfer must return false if fails, there is no provision for failure to revert, and some tokens will not revert resulting in silent transfer success.

## Impact

The protocol believes that the transfer successful, resulting in the loss of funds.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L171
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67

## Tool used

Manual Review

## Recommendation

Use safeTransfer instead of transfer
