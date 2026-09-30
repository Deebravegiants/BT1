# [C] Previous rewardRate is removed when periodFinish has not yet been reached

## Summary
Severity: Critical
Contest weight: 0.4138
Dataset id: 4139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When incentivizeRecurPool is called and the periodFinish has not yet been reached, it incorrectly sets newRewardRate, which consists of only the new incentiveAmount, to state.rewardRate instead of adding it to state.rewardRate.
```solidity
function incentivizeRecurPool(
    RecurIncentiveParams[] calldata params,
    address incentiveToken
) external returns (uint256 totalIncentiveAmount) {
    // ...
    // record new reward
    uint256 newRewardRate;
    if (block.timestamp >= periodFinish) {
        // current period is over
        // uint256 internal constant REWARD_RATE_PRECISION = 1e6;
        newRewardRate = params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, key.duration);
        state.rewardRate = newRewardRate;
        state.lastUpdateTime = uint64(block.timestamp);
        state.periodFinish = uint64(block.timestamp + key.duration);
    } else {
        // period is still active
        // add the new reward to the existing period
        uint256 remaining = periodFinish - block.timestamp;
        // @audit - this is removing previous rewardRate
        newRewardRate += params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, remaining);
        state.rewardRate = newRewardRate;
        state.lastUpdateTime = uint64(block.timestamp);
        // prevent overflow when computing rewardPerToken
        if (newRewardRate >= ((type(uint256).max / PRECISION_DIV_REWARD_RATE_PRECISION) / key.duration)) {
            revert MasterBunni__AmountTooLarge();
        }
    }
    totalIncentiveAmount += params[i].incentiveAmount;
    // ...
}
```
This effectively removes the previous rewardRate from the other incentive provider, causing the reward to be lost.

## Recommendation
Add the newRewardRate to state.rewardRate, instead of replacing state.rewardRate with newRewardRate.
```solidity
function incentivizeRecurPool(
    RecurIncentiveParams[] calldata params,
    address incentiveToken
) external returns (uint256 totalIncentiveAmount) {
    // ...
    // record new reward
    uint256 newRewardRate;
    if (block.timestamp >= periodFinish) {
        // current period is over
        // uint256 internal constant REWARD_RATE_PRECISION = 1e6;
        newRewardRate = params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, key.duration);
        state.rewardRate = newRewardRate;
        state.lastUpdateTime = uint64(block.timestamp);
        state.periodFinish = uint64(block.timestamp + key.duration);
    } else {
        // period is still active
        // add the new reward to the existing period
        uint256 remaining = periodFinish - block.timestamp;
        // @audit - this is removing previous rewardRate
        newRewardRate += params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, remaining);
        state.rewardRate += newRewardRate;
        state.lastUpdateTime = uint64(block.timestamp);
        // prevent overflow when computing rewardPerToken
        if (newRewardRate >= ((type(uint256).max / PRECISION_DIV_REWARD_RATE_PRECISION) / key.duration)) {
            revert MasterBunni__AmountTooLarge();
        }
    }
    totalIncentiveAmount += params[i].incentiveAmount;
    // ...
}
```
