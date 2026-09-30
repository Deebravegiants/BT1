# [M] `MasterChef.updatePool

## Summary
Severity: Medium
Contest weight: 0.4853
Dataset id: 1582
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `updatePool` function intends to calculate the accumulated Concur rewards by tracking the number of blocks passed since the last update to correctly determine how many Concur tokens to distribute to each share. The reward distribution has a start and end block which dictates the timeframe by which rewards will be distributed to the underlying pool.

If a pool has not recently updated itself and has reached the `block.number >= endBlock` statement in `updatePool`, then any rewards that it would normally be entitled to prior to reaching `endBlock` will not be attributed to the pool. Therefore, once rewards are no longer being distributed, pools who had not recently called `updatePool` before reaching `endBlock` are at a disadvantage as compared to more active pools.

## Proof of Concept
[MasterChef.sol#L135-L154](https://github.com/code-423n4/2022-02-concur/blob/main/contracts/MasterChef.sol#L135-L154)
```solidity
// Update reward variables of the given pool to be up-to-date.
function updatePool(uint _pid) public {
    PoolInfo storage pool = poolInfo[_pid];
    if (block.number <= pool.lastRewardBlock) {
        return;
    }
    uint lpSupply = pool.depositToken.balanceOf(address(this));
    if (lpSupply == 0 || pool.allocPoint == 0) {
        pool.lastRewardBlock = block.number;
        return;
    }
    if(block.number >= endBlock) {
        pool.lastRewardBlock = block.number;
        return;
    }        
    
    uint multiplier = getMultiplier(pool.lastRewardBlock, block.number);
    uint concurReward = multiplier.mul(concurPerBlock).mul(pool.allocPoint).div(totalAllocPoint);
    pool.accConcurPerShare = pool.accConcurPerShare.add(concurReward.mul(_concurShareMultiplier).div(lpSupply));
    pool.lastRewardBlock = block.number;
}
```

## Recommendation
Ensure that once the `block.number >= endBlock` statement has been reached, the `pool.accConcurPerShare` is updated to reflect the number of blocks that have passed up until `endBlock`. The number of blocks should be equal to `endBlock - pool.lastRewardBlock`. This will ensure stale pools are not negatively impacted once `endBlock` has been reached by the contract.

The warden has identified a way in which the contract will not release rewards that are due for a depositor.

Because the check doesn’t accrue until the last eligible block, the reward loss can be quantified as:  
LastTimeAccrueBeforeEndBlock - endBlock

The finding is valid, but because it pertains to loss of yield, and because the loss can be quantified and reduced by simply calling at the last available block, I believe Medium Severity to be more appropriate.
