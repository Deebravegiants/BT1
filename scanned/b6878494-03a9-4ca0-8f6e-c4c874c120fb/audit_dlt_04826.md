# [H] Wrong logic in `roll()`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/7
Type: sherlock-finding

## Details
yixxas

high

# Wrong logic in `roll()`

## Summary
Wrong logic in `roll()` causes the function to revert after cooldown period has elapsed.

## Vulnerability Detail
The check for `if (lastSettle + cooldown > block.timestamp)` should be `if (lastSettle + cooldown < block.timestamp)` instead. We want to revert only if the `lastSettle` time plus `cooldown` period has not exceeded current time.

## Impact
This issue breaks the rolling mechanism introduced by sense finance - high severity.

## Code Snippet
https://github.com/sense-finance/auto-roller/blob/b3f33b70aafeed108c1505271bf1301df4ae2d45/src/AutoRoller.sol#L161

## Tool used

Manual Review

## Recommendation
Change to `if (lastSettle + cooldown < block.timestamp)`.
