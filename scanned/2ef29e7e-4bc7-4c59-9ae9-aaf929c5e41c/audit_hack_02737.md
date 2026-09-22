# [M] `ERC20.approve()` is missing the return value check.

## Summary
Severity: Medium
Reporter: hansfriese
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204
Type: audit-issue

## Details
# `ERC20.approve()` is missing the return value check.

## Summary
`ERC20.approve()` is missing the return value check.

## Vulnerability Detail
`ERC20.approve()` is missing the return value check.

Some `ERC20` tokens don't revert if the approval is failed but return `false` instead.

In this protocol, there is no special requirements of `ERC20` token and it migth work unexpectedly with such weird tokens.

## Impact
With the tokens that don't actually perform the approve and return `false` are still counted as a correct approve.

## Code Snippet
- https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204
- https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L300

## Tool used
Manual Review

## Recommendation
Recommend using `OpenZeppelin's SafeERC20` library with the `safeIncreaseAllowance()` and `safeDecreaseAllowance`.
