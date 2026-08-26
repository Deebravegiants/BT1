# [M] Changing `ERC20ConvictionScore.governanceThreshold` leads to temporarily broken state

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-26
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/39
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details

Changing the `governanceThreshold` breaks the governance credit score accounting as users who currently qualify for being a governor may not qualify anymore and this influences the `quorum` threshold.
It can be changed using `FSD.updateGovernanceThreshold`.

## Impact
Imagine, governance calls `updateGovernanceThreshold` with a higher value disqualifying current governors but their `ERC20ConvictionScore.isGovernance[user]` state is not yet updated.
Someone creates a proposal using the old higher threshold.

Someone updates the user states now, for example, by transferring a single wei to them, their status is reset in `_updateConvictionScore` and the quorum threshold might be unreachable by the updated collective of governors.
The proposal needs to be cancelled, all users' `isGovernance` state needs to be updated to arrive at the correct `totalVotes` again.

## Recommended Mitigation Steps

I don't see a good solution in the current design.
If possible make `governanceThreshold` a constant or manually update all users' state after a change such that the `totalVotes` are correct again.
