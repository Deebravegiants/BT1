# [M] Revisited Logic to Distribute WOM emissions in MasterWombat

## Summary
Severity: Medium
Contest weight: 0.5943
Dataset id: 13415
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Wombat protocol introduces a new emissions distribution mechanism, which allows the veWOM holders to vote on how WOM emissions can be distributed to diﬀerent gauges according to the allocation and voting weight. The MasterWombatV3 contract is responsible to claim WOM emissions from the Voter contract and distribute them to users. To elaborate, we show below the code snippet of the _updatePool() routine, which is invoked at the beginning of each operation (e.g., deposit/withdraw) to claim WOM emissions from the Voter contract and accumulate the accWomPerShare/ accWomPerFactorShare. By design, the new claimed emissions shall be rewarded into the next reward duration. However, current implementation invokes the IVoter(voter).distribute() (line 218) ﬁrst to claim the emissions and update the rewardRate, then invokes the calRewardPerUnit() (line 221) to accumulate the accWomPerShare/ accWomPerFactorShare. As a result, the accWomPerShare/accWomPerFactorShare are accumulated per the new rewardRate, not the expected old rewardRate. Our analysis shows that it shall accumulate the accWomPerShare/accWomPerFactorShare before the claiming of new emissions in the _updatePool() routine.
```solidity
function _updatePool(uint256 _pid) private {
    PoolInfo storage pool = poolInfo[_pid];
    IVoter(voter).distribute(address(pool.lpToken));
    if (block.timestamp > pool.lastRewardTimestamp) {
        (uint256 accWomPerShare, uint256 accWomPerFactorShare) = calRewardPerUnit(_pid);
        pool.accWomPerShare = to104(accWomPerShare);
        pool.accWomPerFactorShare = to104(accWomPerFactorShare);
        pool.lastRewardTimestamp = uint40(lastTimeRewardApplicable(pool.periodFinish));
    }
}
```
Moreover, the notifyRewardAmount() routine is invoked indirectly from the Voter::distribute() routine. It is used to notify the MasterWombatV3 contract to update the pool.rewardRate and the pool.periodFinish. However, it comes to our attention that it also updates the pool.lastRewardTimestamp to block.timestamp. As a result, it bypasses the accumulation of the accWomPerShare/ accWomPerFactorShare in the _updatePool() routine, as the condition if (block.timestamp > pool.lastRewardTimestamp) (line 220) becomes false.
```solidity
function notifyRewardAmount(address _lpToken, uint256 _amount) external override {
    require(_amount > 0, "notifyRewardAmount: zero amount");
    // this line reverts if asset is not in the list
    uint256 pid = assetPid[_lpToken] - 1;
    PoolInfo storage pool = poolInfo[pid];
    if (block.timestamp >= pool.periodFinish) {
        pool.rewardRate = to128(_amount / REWARD_DURATION);
    } else {
        uint256 remainingTime = pool.periodFinish - block.timestamp;
        uint256 leftoverReward = remainingTime * pool.rewardRate;
        pool.rewardRate = to128((_amount + leftoverReward) / REWARD_DURATION);
    }
    pool.lastRewardTimestamp = uint40(block.timestamp);
    pool.periodFinish = uint40(block.timestamp + REWARD_DURATION);
}
```

## Recommendation
Revisit the above mentioned logic to accumulate the accWomPerShare/accWomPerFactorShare ﬁrst per current reward rate, then claim the new emissions for the next reward duration.
