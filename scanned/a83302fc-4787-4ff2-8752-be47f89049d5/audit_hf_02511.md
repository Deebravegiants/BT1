# [M] Timely _updateReward() in addRewardToken()

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 13406
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Wombat protocol, the MultiRewarderPerSec contract provides an incentive mechanism that rewards the staking of supported assets in MasterWombatV2. The rewards are carried out by adding reward token with a speciﬁc reward speed into the rewarder, and one rewarder can support multiple reward tokens. The staking users are rewarded in each reward token with the speciﬁed reward speed per their deposit amount in MasterWombatV2. The reward token can be dynamically added via addRewardToken() by the owner. When analyzing the logic to add new reward token in the updateMultiplier() routine, we notice the need of timely invoking _updateReward() to update the lastRewardTimestamp before the new reward token gets eﬀective.
```solidity
function addRewardToken(IERC20 _rewardToken, uint96 _tokenPerSec) external onlyOwner {
    // use non-zero amount for accTokenPerShare as we want to check if user
    // has activated the pool by checking rewardDebt > 0
    RewardInfo memory reward = RewardInfo({
        rewardToken: _rewardToken,
        tokenPerSec: _tokenPerSec,
        accTokenPerShare: 1e18
    });
    rewardInfo.push(reward);
    emit RewardRateUpdated(address(_rewardToken), 0, _tokenPerSec);
}
/// @dev This function should be called before lpSupply and sumOfFactors update
function _updateReward() internal {
    uint256 length = rewardInfo.length;
    uint256 lpSupply = lpToken.balanceOf(address(masterWombat));
    if (block.timestamp > lastRewardTimestamp && lpSupply > 0) {
        for (uint256 i; i < length; ++i) {
            RewardInfo storage reward = rewardInfo[i];
            uint256 timeElapsed = block.timestamp - lastRewardTimestamp;
            uint256 tokenReward = timeElapsed * reward.tokenPerSec;
            reward.accTokenPerShare = toUint128((tokenReward * ACC_TOKEN_PRECISION) / lpSupply);
            lastRewardTimestamp = block.timestamp;
        }
    }
}
```
If the call to _updateReward() is not immediately invoked before the new reward token gets eﬀective, the reward in the new reward token will be accumulated from the old lastRewardTimestamp which is the time when the _updateReward() is last invoked. As a result, staking users will get more rewards in the new reward token than expected.

## Recommendation
Timely invoke _updateReward() in the addRewardToken() routine.
