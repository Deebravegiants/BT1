# [M] TrueFiStrategy: Staking rewards can be lost when strategy is removed

## Summary
Severity: Medium
Reporter: Lambda
Source: https://github.com/trusttoken/contracts-pre22/blob/76854d53c5036777286d4392495ef28cd5c5173a/contracts/truefi2/TrueMultiFarm.sol#L148
Type: audit-issue

## Details
# TrueFiStrategy: Staking rewards can be lost when strategy is removed

## Summary
When a strategy is removed / replaced, it is checked that the balance is zero to avoid that any tokens are lost. However, because the balance does not include staking rewards and they are not automatically claimed for `TrueFiStrategy`, it can happen that the rewards are lost.

## Vulnerability Detail
`liquidExit` calls [`unstake`](https://github.com/trusttoken/contracts-pre22/blob/76854d53c5036777286d4392495ef28cd5c5173a/contracts/truefi2/TrueMultiFarm.sol#L148) on the farm. In contrast to [`exit`](https://github.com/trusttoken/contracts-pre22/blob/76854d53c5036777286d4392495ef28cd5c5173a/contracts/truefi2/TrueMultiFarm.sol#L170), this does not claim the rewards.

## Impact
Before the `TrueFiStrategy` is removed, an owner calls `liquidExit` with the whole balance. `_balanceOf` returns 0 afterwards, but there are still staking rewards that could be claimed.

## Code Snippet
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L179
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/base/BaseStrategy.sol#L39

## Tool used

Manual Review

## Recommendation
Call `exit` on the farm instead of `unstake` within `TrueFiStrategy.liquidExit`.
