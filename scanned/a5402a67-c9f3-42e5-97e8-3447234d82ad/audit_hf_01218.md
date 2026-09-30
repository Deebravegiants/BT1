# [M] StakingContract.setRewardsDuration can be DoS'd

## Summary
Severity: Medium
Contest weight: 0.1046
Dataset id: 5454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The  
StakingRewards.setRewardsDuration  
function  
can  
only  
be  
called  
after  
periodFinish. However,  
anyone  
can  
call  
VestedRewardsDistribution.distribute  
which  
calls  
StakingReward.notifyRewardAmount and sets a new periodFinish. It's unlikely that the rewardDuration  
can ever be changed as long as the DssVest is still active.

## Recommendation
Be aware that you're unlikely to be able to change the rewardsDuration once the  
DssVest vesting starts. Alternatively, allow changing the rewards duration even before the current period  
finishes by adding reward rebasing logic to the setRewardsDuration by:  
1. Accumulating the current rewards via updateReward(address(0)).  
2. Calculating the old reward leftover.  
3. Changing the rewardsDuration.  
4. Setting the new rewardRate over the new duration, and setting the new periodFinish and lastUp-  
dateTime.  
There is currently a workaround by first calling setRewardsDistribution(address(0)) to disable noti-  
fyRewardAmount calls, and waiting until the period is over. Then setRewardsDuration can be called, and  
the rewards distribution contract can be set again. However, this leads to non-smooth reward distribu-  
tions.
