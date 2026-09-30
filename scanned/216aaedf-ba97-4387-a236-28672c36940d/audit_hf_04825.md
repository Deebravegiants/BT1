# [H] cannot forward extra rewards from both OCY_Convex_A and OCY_Convex_B

## Summary
Severity: High
Contest weight: 0.6002
Dataset id: 22705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Convex specifies rewardContract to be a VirtualBalanceRewardPool, but all three OCY_Convex uses it as a ERC20 token, which make it impossible to claim extra rewards and forward them to the OCT_YDL. According to Convex doc:

The BaseRewardPool has an array of child reward contracts called extraRewards. You can query the number of extra rewards via baseRewardPool.extraRewardsLength(). This array holds a list of VirtualBalanceRewardPool contracts which are similar in nature to the base reward contract but without actual control of staked tokens. This means that if a pool has CRV rewards as well as SNX rewards, the pool's main reward contract(BaseRewardPool) will distribute the CRV and the child contract(VirtualBalanceRewardPool) will distribute the SNX.

But, in current implementation: (take OCY_Convex_A for example)

```solidity
// Extra Rewards
if (extra) {
uint256 extraRewardsLength =
IBaseRewardPool_OCY_Convex_A(convexRewards).extraRewardsLength();
for (uint256 i = 0; i < extraRewardsLength; i++) {
address rewardContract =
IBaseRewardPool_OCY_Convex_A(convexRewards).extraRewards(i);
uint256 rewardAmount =
IBaseRewardPool_OCY_Convex_A(rewardContract).rewardToken().balanceOf(
address(this)
);
if (rewardAmount > 0) { IERC20(rewardContract).safeTransfer(OCT_YDL, rewardAmount); }
}
}
```

Tokens cannot be sent to YDL. Current OCY_Convex_A, OCY_Convex_B and OCY_Convex_C cannot forward extraRewards to YDL.

## Recommendation
Use the real token address for token transfer.
