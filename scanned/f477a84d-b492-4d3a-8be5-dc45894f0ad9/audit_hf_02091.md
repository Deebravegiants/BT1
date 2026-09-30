# [M] Potential Overﬂow Mitigation in notifyRewardAmount()

## Summary
Severity: Medium
Contest weight: 0.4613
Dataset id: 11800
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ChocolateCash protocol has a built-in incentivizer mechanism, which is based on the popular StakingRewards from Synthetix. In this section, we focus on a routine, i.e., rewardPerToken(), which is responsible for calculating the reward rate for each staked token and it is part of the updateReward modiﬁer that would be invoked up-front for almost every public function in Boardroom to update and use the latest reward rate. The reason is due to the known potential overﬂow pitfall when a new oversized reward amount is added into the pool. In particular, as the rewardPerToken() routine involves the multiplication of three uint256 integer, it is possible for their multiplication to have an undesirable overﬂow (lines 61 67), especially when the rewardRate is largely controlled by an external entity, i.e., rewardDistribution (through the notifyRewardAmount() function).
```solidity
function lastTimeRewardApplicable() public view returns (uint256) {
    return Math.min(block.timestamp, periodFinish);
}

function rewardPerToken() public view returns (uint256) {
    if (totalSupply() == 0) return rewardPerTokenStored;
    return rewardPerTokenStored.add(
        lastTimeRewardApplicable()
            .sub(lastUpdateTime)
            .mul(rewardRate)
            .mul(1e18)
            .div(totalSupply())
    );
}

function notifyRewardAmount(uint256 reward)
    override
    external
    onlyRewardDistribution
{
    updateReward(address(0));
    if (block.timestamp >= periodFinish) {
        rewardRate = reward.div(DURATION);
    } else {
        uint256 remaining = periodFinish.sub(block.timestamp);
        uint256 leftover = remaining.mul(rewardRate);
        rewardRate = reward.add(leftover).div(DURATION);
    }
    lastUpdateTime = block.timestamp;
    periodFinish = block.timestamp.add(DURATION);
    emit RewardAdded(reward);
}
```
Apparently, this issue is made possible if the reward amount is given as the argument to notifyRewardAmount() such that the calculation of rewardRate.mul(1e18) always overﬂows, hence locking all deposited funds! Note that an authentication check on the caller of notifyRewardAmount() greatly alleviates such concern. Currently, only the rewardDistribution address is able to call notifyRewardAmount() and this address is set by the owner. Apparently, if the owner is a normal address, it may put users funds at risk. To mitigate this issue, it is necessary to have the ownership under the governance control and ensure the given reward amount will not be oversized to overﬂow and lock users funds.

## Recommendation
Be consistent and suﬃcient in mitigating the potential overﬂow risk in all aﬀected pools, including Boardroom, MigrationPool, ReferPool, and LLCUSDTLPTokenSharePool.
