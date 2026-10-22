# [M] Incorrect Liquidity Mining in DackieV3LmPool

## Summary
Severity: Medium
Contest weight: 0.5974
Dataset id: 11852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DackieSwap protocol features a liquidity mining support with Pancake V3 NFT-like positions. In the process of examining the actual implementation, we notice a potential issue that may block a legitimate user from claiming the rewards. To elaborate, we show below the implementation of the related getRewardGrowthInside() routine. As the name indicates, this routine is used to compute the reward growth data. However, it does not consider a possible underflow situation that may make the associated MasterChef V3 smart contract unable to calculate reward for the positions whose initial rewardGrowthInsideX128 values were negative underflow.
```solidity
function getRewardGrowthInside(
    mapping(int24 => LmTick.Info) storage self,
    int24 tickLower,
    int24 tickUpper,
    int24 tickCurrent,
    uint256 rewardGrowthGlobalX128
) internal view returns (uint256 rewardGrowthInsideX128) {
    LmTick.Info storage lower = self[tickLower];
    LmTick.Info storage upper = self[tickUpper];
    // calculate reward growth below
    uint256 rewardGrowthBelowX128;
    if (tickCurrent >= tickLower) {
        rewardGrowthBelowX128 = lower.rewardGrowthOutsideX128;
    } else {
        rewardGrowthBelowX128 = rewardGrowthGlobalX128 - lower.rewardGrowthOutsideX128;
    }
    // calculate reward growth above
    uint256 rewardGrowthAboveX128;
    if (tickCurrent < tickUpper) {
        rewardGrowthAboveX128 = upper.rewardGrowthOutsideX128;
    } else {
        rewardGrowthAboveX128 = rewardGrowthGlobalX128 - upper.rewardGrowthOutsideX128;
    }
    rewardGrowthInsideX128 = rewardGrowthGlobalX128 - rewardGrowthBelowX128 - rewardGrowthAboveX128;
}
```

## Recommendation
Revisit the above getRewardGrowthInside() routine to handle the possible underflow situation. Here comes a possible extension to check whether an underflow situation occurs:
```solidity
function _getRewardGrowthInsideInternal(
    int24 tickLower,
    int24 tickUpper
) internal view returns (uint256 rewardGrowthInsideX128, bool isNegative) {
    (, int24 tick, , , , , ) = pool.slot0();
    LmTick.Info memory lower = lmTicks[tickLower];
    LmTick.Info memory upper = lmTicks[tickUpper];
    // calculate reward growth below
    uint256 rewardGrowthBelowX128;
    if (tick >= tickLower) {
        rewardGrowthBelowX128 = lower.rewardGrowthOutsideX128;
    } else {
        rewardGrowthBelowX128 = rewardGrowthGlobalX128 - lower.rewardGrowthOutsideX128;
    }
    // calculate reward growth above
    uint256 rewardGrowthAboveX128;
    if (tick < tickUpper) {
        rewardGrowthAboveX128 = upper.rewardGrowthOutsideX128;
    } else {
        rewardGrowthAboveX128 = rewardGrowthGlobalX128 - upper.rewardGrowthOutsideX128;
    }
    rewardGrowthInsideX128 = rewardGrowthGlobalX128 - rewardGrowthBelowX128 - rewardGrowthAboveX128;
    isNegative = (rewardGrowthBelowX128 + rewardGrowthAboveX128) > rewardGrowthGlobalX128;
}
```
