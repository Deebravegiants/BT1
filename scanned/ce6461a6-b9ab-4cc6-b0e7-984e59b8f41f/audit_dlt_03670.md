# [M] It's not possible to claim MergingPool rewards for the last round, only for rounds previous to it

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-10
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/7
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/MergingPool.sol#L153


# Vulnerability details

### C4 issue
M-04: [DoS in MergingPool::claimRewards function and potential DoS in RankedBattle::claimNRN function if called after a significant amount of rounds passed](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/868)

### Comments
Previously, The `MergingPool::claimRewards` function loop could exceed the block gas limit, potentially causing a DoS. This would happen if a user tried claiming their rewards after too many rounds had passed. Similarly, there was a risk of DoS in `RankedBattle::claimNRN` for the same reason.

In both cases, rounds were iterated up to the current round ID non inclusively.

### Mitigation
[PR #18](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/18)
Now the issue in both functions is fixed thanks to an additional input `uint32 totalRoundsToConsider` which allows users to loop fewer rounds per call. However, the input validation of `totalRoundsToConsider` in `MergingPool::claimRewards` is incorrect:

```solidity
    require(lowerBound + totalRoundsToConsider < roundId, "MergingPool: totalRoundsToConsider exceeds the limit");
    uint8 generation = _fighterFarmInstance.generation(0);
    for (uint32 currentRound = lowerBound; currentRound < lowerBound + totalRoundsToConsider; currentRound++) {
```

`lowerBound + totalRoundsToConsider` can at most be equal to `roundId - 1`, which means that claimRewards() will loop, at most, till `roundId - 2`. Therefore, it's not possible to claim MergingPool rewards for the last round, only for rounds previous to it.

Note that this was [correctly implemented](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/RankedBattle.sol#L333) in the `RankedBattle::claimNRN` fix.

### Suggestion
Change
```solidity
    require(lowerBound + totalRoundsToConsider < roundId, "MergingPool: totalRoundsToConsider exceeds the limit");
```
to
```solidity
    require(lowerBound + totalRoundsToConsider <= roundId, "MergingPool: totalRoundsToConsider exceeds the limit");
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/7_
