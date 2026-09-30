# [M] Timely massUpdatePools During Pool Weight Changes

## Summary
Severity: Medium
Contest weight: 0.4345
Dataset id: 11632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ArthSwap MasterChef protocol provides an incentive mechanism that rewards the staking of the supported assets with the ARSW token.
The rewards are carried out by designating a number of staking pools into which supported assets can be staked.
And staking users are rewarded in proportional to their share of LP tokens in the reward pool.
The reward pools can be dynamically added via add() and the weights of the supported pools can be adjusted via set().
When analyzing the pool weight update routine set(), we notice the need of timely invoking massUpdatePools() to update the reward distribution before the new pool weight becomes effective.
```solidity
function set(
    uint256 pid,
    uint256 allocPoint,
    IRewarder rewarder,
    bool overwrite
) external onlyOwner {
    totalAllocPoint = totalAllocPoint.sub(poolInfos[pid].allocPoint).add(
        allocPoint
    );
    poolInfos[pid].allocPoint = allocPoint.to64();
    if (overwrite) {
        rewarders[pid] = rewarder;
    }
    emit LogSetPool(
        pid,
        allocPoint,
        overwrite ? rewarder : rewarders[pid],
        overwrite
    );
}
```
If the call to massUpdatePools() is not immediately invoked before updating the pool weights, certain situations may be crafted to create an unfair reward distribution.
Moreover, a hidden pool without any weight can suddenly surface to claim unreasonable share of rewarded tokens.
Given this, we suggest to invoke massUpdatePools() immediately before the pool weights update.

## Recommendation
Timely invoke massUpdatePools() when any pool's weight has been updated.
