# [M] Emission schedule is not followed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-07-loopfi
Published: 2024-08-15
Source: https://github.com/code-423n4/2024-07-loopfi-findings/issues/104
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-loopfi/blob/57871f64bdea450c1f04c9a53dc1a78223719164/src/reward/ChefIncentivesController.sol#L989


# Vulnerability details

## Impact
Emission schedule is not followed and can cause unexpected allocation of rewards

## Proof of Concept
Whenever a new emission schedule is to be followed ie. block.timestamp becomes greater than the startOffset of the schedule, the `setScheduledRewardsPerSecond` function invokes the `_massUpdatePools` function in order to bring the pools to the latest state

```solidity
    function setScheduledRewardsPerSecond() internal {
        if (!persistRewardsPerSecond) {
            uint256 length = emissionSchedule.length;
            uint256 i = emissionScheduleIndex;
            uint128 offset = uint128(block.timestamp - startTime);
            for (; i < length && offset >= emissionSchedule[i].startTimeOffset; ) {
                unchecked {
                    i++;
                }
            }
            if (i > emissionScheduleIndex) {
                emissionScheduleIndex = i;
=>              _massUpdatePools();
                rewardsPerSecond = uint256(emissionSchedule[i - 1].rewardsPerSecond);
            }
        }
```

But inside the `_massUpdatePools`, the previous `rewardsPerSecond` is used until block.timestamp instead of the startOffset of the new schedule ie. the correct update of `oldRewardsPerSecond * (newScheduleStartTimestamp - lastUpdateStamp) + newRewardsPerSecond * (block.timestamp - newScheduleStartTimestamp)` is not used

_massUpdatePools -> _updatePool -> _newRewards

```solidity
    function _newRewards(
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-07-loopfi-findings/issues/104_
