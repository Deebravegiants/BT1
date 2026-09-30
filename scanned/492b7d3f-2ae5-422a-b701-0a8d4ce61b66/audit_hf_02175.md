# [M] Timely updateReward() Upon the rewardRate Change

## Summary
Severity: Medium
Contest weight: 0.4477
Dataset id: 12129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GoldRoom protocol provides incentive mechanisms that reward the staking of supported assets. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. And staking users are rewarded in proportional to their share of LP tokens in the reward pool. The reward rate can be dynamically conﬁgured via a speciﬁc routine setRewardRate(). When analyzing the speciﬁc routine, we notice the need of timely invoking updateReward() to update the reward distribution before the new rewardRate becomes eﬀective.
```solidity
function setRewardRate(uint256 _new_rate) external onlyByOwnerOrGovernance {
    rewardRate = _new_rate;
}
function setOwnerAndTimelock(address _new_timelock) external onlyByOwnerOrGovernance {
    timelock_address = _new_timelock;
}

// MODIFIERS
modifier updateReward(address account) {
    // Need to retro-adjust some things if the period hasn't been renewed, then start a new one
    if (block.timestamp > periodFinish) {
        retroCatchUp();
    } else {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = lastTimeRewardApplicable();
    }
    if (account != address(0)) {
        rewards[account] = earned(account);
        userRewardPerTokenPaid[account] = rewardPerTokenStored;
    }
}
```
If the call to updateReward() is not immediately invoked before updating the new rewardRate, the rewards may not be accrued using the right rewardRate. In particular, earlier time intervals may be wrongfully using the new rewardRate! Fortunately, this interface is restricted to the authorized entities (via the onlyByOwnerOrGovernance modiﬁer), which greatly alleviates the concern.

## Recommendation
Timely invoke updateReward() when the rewardRate is updated. Also, keep in mind that the current contract does not support deﬂationary tokens! A vetting process needs to be in place to ensure incompatible deﬂationary tokens will not be supported as the staking token for reward.
