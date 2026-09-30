# [M] The VeTranche.getTotalLockP

## Summary
Severity: Medium
Contest weight: 0.5789
Dataset id: 1780
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getTotalLockPoints() function does not return totalLockPoints; instead, it returns totalLockPoints/_PRECISION. This leads to a loss of precision when calculating rewards. ON, not totalLockPoints. This is a source of precision loss.  
```solidity
function getTotalLockPoints() public view override returns (uint256) {
    return totalLockPoints/_PRECISION;
}
```
Let's consider the following scenario:  
1. Lock points:  
• Alice: 10e12  
• Bob: 8e12+9e5  
• totalLockPoints: 18e12+9e5  
• getTotalLockPoints() returns: (18e12+9e5)/1e6=18e6  
2. 180e6 rewards are distributed.  
• rewardsDistributedPerSharePerLockPoint=(180e6*1e18)/18e6=10e18  
```solidity
function _distributeRewards(uint256 rewards) internal returns (uint256) {
    rewardsDistributedPerSharePerLockPoint += (rewards * (_PRECISION **3)) / getTotalLockPoints();
    //...
}
```
3. Individual rewards:  
• Alice: 10e18*10e12/1e24=100e6  
• Bob: 10e18*(8e12+9e5)/1e24=80e6+9  
• Needed rewards: 100e6+80e6+9=180e6+9  
```solidity
function _updateReward(uint256 _id) internal {
    if(lastSharePoint[_id] == rewardsDistributedPerSharePerLockPoint ) return;
    uint256 pendingReward = ((rewardsDistributedPerSharePerLockPoint - lastSharePoint[_id]) * tokensByTokenId[_id] * lockMultiplierByTokenId[_id]) / (_PRECISION **4);
    rewardsByTokenId[_id] += pendingReward;
    lastSharePoint[_id] = rewardsDistributedPerSharePerLockPoint;
}
```
As a result, the needed rewards exceed the actual total rewards.  
Internal pre-conditions  
External pre-conditions  
Attack Path  
The needed rewards may exceed the actual total rewards.

## Recommendation
Use totalLockPoints instead of totalLockPoints/_PRECISION.
