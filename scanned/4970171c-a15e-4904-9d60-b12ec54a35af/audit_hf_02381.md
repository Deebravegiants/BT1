# [M] Timely massUpdatePools During Pool Updates

## Summary
Severity: Medium
Contest weight: 0.4374
Dataset id: 12846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rabbit protocol provides incentive mechanisms that reward the staking of supported assets. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. And staking users are rewarded in proportional to their share of LP tokens in the reward pool. The reward pools can be dynamically added via addPool() and the weights of supported pools can be adjusted via setPool(). When analyzing the pool weight update routine setPool(), we notice the need of timely invoking massUpdatePools() to update the reward distribution before the new pool weight becomes effective.
```solidity
// Update the given pool s rabbit allocation point. Can only be called by the owner.
function setPool(
    uint256 _pid,
    uint256 _allocPoint,
    bool _withUpdate
) public override onlyOwner {
    if (_withUpdate) {
        massUpdatePools();
    }
    totalAllocPoint = totalAllocPoint.sub(poolInfo[_pid].allocPoint).add(_allocPoint);
    poolInfo[_pid].allocPoint = _allocPoint;
}
```
If the call to massUpdatePools() is not immediately invoked before updating the pool weights, certain situations may be crafted to create an unfair reward distribution. Moreover, a hidden pool without any weight can suddenly surface to claim unreasonable share of rewarded tokens. Fortunately, this interface is restricted to the owner (via the onlyOwner modifier), which greatly alleviates the concern.

## Recommendation
Timely invoke massUpdatePools() when any pool s weight has been updated. In fact, the third parameter (_withUpdate) to the set() routine can be simply ignored or removed. Also, keep in mind that the current FairLaunch contract does not support deflationary tokens! A vetting process needs to be in place to ensure incompatible deflationary tokens will not be supported as the pool token for farming.
