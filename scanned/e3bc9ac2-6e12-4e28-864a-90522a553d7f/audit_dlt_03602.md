# [M] H-03 MitigationConfirmed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-reserve-mitigation
Published: 2023-09-27
Source: https://github.com/code-423n4/2023-09-reserve-mitigation-findings/issues/5
Type: code-finding

## Details
# Lines of code




# Vulnerability details

In the previous implementation
After shutdown, checkpoints are stopped
`reward.reward_integral_for[user]` No updates resulted in new users getting more rewards
and possible theft of rewards.

# Mitigation
PR 930
Modify that `checkpoints` are already executed, just not call `IRewardStaking(convexPool).getReward(address(this), true);`
the mitigation resolved the original issue.

# Suggestion
Not calling `convexPool.getReward()`, there is a slight loss of rewards for transferred users
the feeling is that there is no need to ignore this call, `convexPool.getReward()` don't revert if shutdown
