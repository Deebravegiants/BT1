# [M] Timely Update Pool Reward During Pool Weight Changes

## Summary
Severity: Medium
Contest weight: 0.4423
Dataset id: 13246
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ThemisEarlyFarming contract provides an incentive mechanism that rewards the staking of supported assets with the rewardToken token. The rewards are carried out by designating a number of staking pools into which supported assets can be staked. And staking users are rewarded in proportional to their share of tokens in the reward pool.
The staking pools can be dynamically added via addPeriodPool() and the weights of supported pools can be adjusted via setPeriodAllocPoint(). When analyzing the pool weight update routine setPeriodAllocPoint(), we notice the need of timely invoking _updatePeriodRewardShare() for all the staking pools to update the reward distribution before the new pool weight becomes effective.
```solidity
function setPeriodAllocPoint(uint256 _periodPoolId, uint256 _allocPoint, bool _misUpdate) external onlyGovernance {
    // todo update all period
    PeriodPool storage _periodPool = periodPools[_periodPoolId];
    uint256 _beforeAllocPoint = _periodPool.allocPoint;
    _periodPool.allocPoint = _allocPoint;
    totalAllocPoint = totalAllocPoint.add(_allocPoint).sub(_beforeAllocPoint);
    if(!_misUpdate){
        for(uint256 i=0;i<periodPools.length;i++){
            _updatePeriodRewardShare(i);
        }
    }
    emit SetPeriodAllocPointEvent(msg.sender, _periodPoolId, _beforeAllocPoint, _allocPoint);
}
```
If the call to _updatePeriodRewardShare() is not immediately invoked before updating the pool weights, certain situations may be crafted to create an unfair reward distribution. Moreover, a hidden pool without any weight can suddenly surface to claim unreasonable share of rewarded tokens.

## Recommendation
Timely invoke _updatePeriodRewardShare() for all the staking pools when any pool's weight has been updated.
