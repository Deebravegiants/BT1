# [M] M-06 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/51
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of M-06: NOT mitigated

## Mitigated issue
[M-06: NFTs can be transferred even if StakeAtRisk remains, so the user's win cannot be recorded on the chain due to underflow, and can recover past losses that can't be recovered(steal protocol's token)](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/137)

There are two possibilities of revert due to underflow triggered in `RankedBattle.updateBattleRecord()`.
1. In `RankedBattle._addResultPoints_()`: [`accumulatedPointsPerAddress[fighterOwner][roundId] -= points`](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/RankedBattle.sol#L486). The impact is that a fighter with accumulated points, which is transferred to a new address cannot be recorded in a loss. 
2. In `StakeAtRisk.reclaimNRN()`: [`amountLost[fighterOwner] -= nrnToReclaim;`](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/StakeAtRisk.sol#L104). The impact is that a fighter with some stake at risk cannot be recorded in a win until it has lost.

Both of the above only apply to the round in which the fighter was transferred.

There was also an impact reported that a transferred fighter could be used to reclaim losses from a previous round. I consider this aspect invalid, since the new owner cannot gain more than the old owner could (re)gain. It might however be considered an issue that a fighter with stake at risk can be transferred since this is almost the same as transferring a staked fighter. This does not quite seem to be the initial issue reported, but it [is fixed anyway by fix 1490](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/14/files#diff-bcde603c412d351d31a22361f1593f9d9ac1e73c65754d4dda3e80033aa0e415R293).

## Mitigation review - mootly mitigated and causes an even worse DoS.
A new variable `addressStartedRound[tokenId][roundId]` has been added, with [a check that reverts if the owner of the `tokenId` has changed from a previous call in the round](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/RankedBattle.sol#L375-L380). That is, only fights under the first owner can be updated.
So this now reverts in a superset of the original cases. It balances the exploitability for profit, but now any fighter transfer will cause a DoS of the game server trying to call `updateBattleRecord()`. If a fighter is transferred then all matches with this fighter will lead to a revert. This can be quite significant. If fighters are paired at random and 10% of fighters have been transferred then over 19% of all matches will revert. Since there is no time in between rounds, this will be an issue whenever a fighter is transferred. The round id is also not emitted when a fighter is transferred so it would be difficult for the game server to fairly exclude transferred fighters.

This is perhaps an error rather than a failed mitigation, but since this error renders the initial issue moot, I leave it here as an unmitigated M-06 rather than reporting it as an error separately.

### Recommended mitigation steps
It seems the intention is to lock a fighter as long as it is staked on, but otherwise freely allow transfers.
`accumulatedPointsPerAddress` and `amountLost` are just convenience variables, and never used for validation. They could simply be removed, or it would make sense to make them signed integers. That would be sufficient to mitigate this underflow revert.

The issue that a fighter can be transferred with stake at risk has been fixed independently [in fix 1490](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/14/files#diff-bcde603c412d351d31a22361f1593f9d9ac1e73c65754d4dda3e80033aa0e415R293), rather than fix 137. Now a fighter has to be completely clear of stake and stake at risk in order to be transferred.

Thus removing the [`addressStartedRound` check](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/RankedBattle.sol#L375-L380) and instead making `accumulatedPointsPerAddress` and `amountLost` signed integers, or just removing them, solves all these issues related to M-06.
