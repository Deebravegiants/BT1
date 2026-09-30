# [M] Upgraded Q -> 2 from #39 [1713839723115]

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-23
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/71
Type: code-finding

## Details
Judge has assessed an item in Issue #39 as 2 risk. The relevant finding follows:

 Medium issue 2
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/RankedBattle.sol#L206-L210
Staking and unstaking is controlled in unison. If staking is possible during the battles, the only way to halt staking it is therefore to also halt unstaking. Users may thus stake during the battles and then suddenly not be able to unstake. It seems that if it was possible to stake during the battles it should always be possible to unstake again.
Contrast this with staking and unstaking outside of battles where users can be expected to make up their minds about how much they want to stake before the battles start, and then be committed to this stake (i.e. allowedStakingDuringRanked remains false).
Being allowed to stake during battles should be interpreted as an added opportunity for the user, with an added risk. The opportunity should not be possible to revoke without also allowing the user to withdraw from the added risk.

Consider not allowing a true allowedStakingDuringRanked be set to false while rankedOpen == true. This way the admin's decision to allow staking during battles will always allow users to unstake until the end of the battles.
