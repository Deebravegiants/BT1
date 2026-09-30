# [M] Rewards are permanently locked when totalSupply = 0 in RecurPools

## Summary
Severity: Medium
Contest weight: 0.5716
Dataset id: 4156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _rewardPerToken(
    uint256 rewardPerTokenStored,
    uint256 totalSupply,
    uint256 lastTimeRewardApplicable,
    uint256 lastUpdateTime,
    uint256 rewardRate
) internal pure returns (uint256) {
    if (totalSupply == 0) {
        return rewardPerTokenStored; // @audit rewardPerTokenStored isn't
        // updated but lastUpdateTime is updated
    }
    // mulDiv won't overflow since we check that rewardRate is less than
    // (type(uint256).max / PRECISION_DIV_REWARD_RATE_PRECISION / duration)
    return rewardPerTokenStored
        + FixedPointMathLib.mulDiv(
            lastTimeRewardApplicable - lastUpdateTime
        ) * PRECISION_DIV_REWARD_RATE_PRECISION, rewardRate, totalSupply
```
2. After _rewardPerToken is called, the lastUpdateTime is always updated:
```solidity
state.lastUpdateTime = lastTimeRewardApplicable;
```
This means that for any period where the pool has incentives allocated (rewardRate > 0) and the total supply is 0 (no stakers) and time passes between lastUpdateTime and periodFinish, the rewards meant for distribution during this period become permanently locked in the contract as:
They are not distributed to any stakers
There is no mechanism for the incentive depositor to recover them
The time period is marked as processed due to lastUpdateTime being updated

## Recommendation
It's recommended to skip updating lastUpdateTime when totalSupply = 0 to allow the rewards to accumulate for future stakers or allow incentive providers to reclaim undistributed rewards after the period
