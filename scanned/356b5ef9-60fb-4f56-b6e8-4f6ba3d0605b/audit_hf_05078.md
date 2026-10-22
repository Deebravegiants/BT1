# [M] Rewards Can Be Harvested Even When Dis-

## Summary
Severity: Medium
Contest weight: 0.2474
Dataset id: 23094
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the contract StakedEXA.sol the finishDistribution() intends to finish the distribution of the reward token, but it fails to do so. Rewards can still be harvested from the Market and later claimed, meaning, rewards can be distributed violating the finish time of the distribution.  
1.) The finishDistribution() intends to finish the distribution of the reward token, let's assume the admin now wants to finish the distribution, and calls the function --> protocol/contracts/StakedEXA.sol#L425  
Now the finish time is set to the block.timestamp  
2.) All the above function does is transfer reward token to savings address (dependent upon rate and time difference)  
3.) After the finishDistribution(), a normal user can still trigger the harvest() function --> protocol/contracts/StakedEXA.sol#L344  
This would firstly calculate assets to be withdrawn from the market which is dependent on the allowance of the distributor and then the assets are withdrawn from the market. And then notifyRewardAmount() is triggered at the last. protocol/contracts/StakedEXA.sol#L209  
4.) notifyRewardAmount() the reward.rate would be calculated as  
RewardData storage rewardData = rewards[reward];  
if (block.timestamp >= rewardData.finishAt) {  
    rewardData.rate = amount / rewardData.duration;  
}  
Because the finishAt has been marked to the timestamp when finaliseRewards was called.  
5.) And lastly rewardsData is updated  
rewardData.finishAt = uint40(block.timestamp) + rewardData.duration;  
rewardData.updatedAt = uint40(block.timestamp);  
6.) Now the user can claim the rewards since they are harvested, triggering the claim() function  
7.) Even after finalisation of rewards, the reward tokens were distributed from the market and harvested and notified. It can be seen as if provider lost those assets which were not meant to be distributed.  
Rewards still being able to be harvested even after the finalisation of rewards, the provider would loose his assets if had given a infinite approval. The finalise rewards marks the Finishes the distribution of a reward token

## Recommendation
The way to avoid starting a new distribution would be for the provider to set 0 allowances on the market or withdraw the assets
