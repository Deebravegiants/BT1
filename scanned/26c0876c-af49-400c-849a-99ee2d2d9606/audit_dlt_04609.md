# [H] `slash()` can be used to withdraw funds even when protocol is in a paused state

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/46
Type: sherlock-finding

## Details
yixxas

high

# `slash()` can be used to withdraw funds even when protocol is in a paused state

## Summary
`pause()` is used during an emergency situation, and presumably this should stop all transfer of assets of protocol while the situation is figured out. However, users with the `PAUSER_ROLE` can bypass this by calling `slash()` to withdraw their own or assets of others.

## Vulnerability Detail
`slash()` is lacking any sort of `pause` related modifier to it. It can be called regardless of whether the protocol is in a paused state. I understand that `claimAndExitFor()` and `stakeFor()` can also be used to move assets around but these are utilised only during token migration and only allowed by the `RECOVERY_ROLE`.

## Impact
Assets that are supposed to be frozen during the paused state can still be moved around by `PAUSER_ROLE`.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L403

## Tool used

Manual Review

## Recommendation
I recommend adding the `whenNotPaused` modifier to `slash()`.
