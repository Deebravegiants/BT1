# [M] Unused rewards

## Summary
Severity: Medium
Contest weight: 0.6522
Dataset id: 9401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `VE3DRewardPool` and `BaseRewardPool` contract is supposed to distribute rewards to stakers, but if in some period, `totalSupply()` was equal to `0`, then for that time period, rewards will not be added to `rewardPerTokenStored` and those period rewards would not distribute to any address and those rewards will stuck in contract forever.

## Proof of Concept
This is `notifyRewardAmount()` code in `BaseRewardPool` contract: (`VE3DRewardPool` code is similar)
```solidity
function notifyRewardAmount(uint256 reward) internal updateReward(address(0)) {
    historicalRewards = historicalRewards.add(reward);
    if (block.timestamp >= periodFinish) {
        rewardRate = reward.div(duration);
    } else {
        uint256 remaining = periodFinish.sub(block.timestamp);
        uint256 leftover = remaining.mul(rewardRate);
        reward = reward.add(leftover);
        rewardRate = reward.div(duration);
    }
    currentRewards = reward;
    lastUpdateTime = block.timestamp;
    periodFinish = block.timestamp.add(duration);
    emit RewardAdded(reward);
}
```

As you can see, in the line `rewardRate = reward.div(duration);` the value of `rewardRate` has been set to the division of available `reward` to `duration`. So if we distribute `rewardRate` amount in every second between stakers, then all rewards will be used by contract. Contract uses `updateReward()` modifier to update `rewardPerTokenStored` (this variable keeps track of distributed tokens) and this modifier uses `rewardPerToken()` to update `BaseRewardPool`:
```solidity
modifier updateReward(address account) {
    rewardPerTokenStored = rewardPerToken();
    lastUpdateTime = lastTimeRewardApplicable();
    if (account != address(0)) {
        rewards[account] = earned(account);
        userRewardPerTokenPaid[account] = rewardPerTokenStored;
    }
    emit RewardUpdated(account, rewards[account], rewardPerTokenStored, lastUpdateTime);
    _;
}
```

This is `rewardPerToken()` code in `BaseRewardPool`:
```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalSupply() == 0) {
        return rewardPerTokenStored;
    }
    return
        rewardPerTokenStored.add(
            lastTimeRewardApplicable().sub(lastUpdateTime).mul(rewardRate).mul(1e18).div(
                totalSupply()
            )
        );
}
```

If for some period `totalSupply()` was `0` then contract won’t increase `rewardPerTokenStored` and those periods reward stuck in contract forever, because there is no mechanism to calculate them and withdraw them in contract. For example if `operator` deploy and initialize the pool immediately before others having a chance of staking their tokens, and use `queueNewRewards()` to queue the rewards then the rewards for early period of pool will be locked forever.

## Recommendation
Add some mechanism to recalculate `rewardRate` or calculated undistributed rewards (calculated undistributed reward based on `rewardRate` and when `totalSupply()` is `0`).

Recover function would solve this issue. Middle risk.

The warden has found a valid problem, however a coded POC would have gone a long way.

In order to judge the issue I had to code it for myself to be able to demonstrate the problem.

Anyhow this is a Brownie dump of me setting up the contract (removing transferFrom to get it done rapidly) Showing how skipping 1/3 of reward duration will cause a loss of 1/3 of the yield.

Meaning that the accumulator used for rewards is not redistributing the old rewards
     
     
     >>> x.lastTimeRewardApplicable()
     0
     >>> x.queueNewRewards(1e18, {"from": a[0]})
     Transaction sent: 0x0b959c886d959038396aa0a9a82cef39c6bc817e4e48026068b242b0a46df81f
       Gas price: 0.0 gwei   Gas limit: 12000000   Nonce: 5
       BaseRewardPool.queueNewRewards confirmed   Block: 15208165   Gas used: 46822 (0.39%)
     
     <Transaction '0x0b959c886d959038396aa0a9a82cef39c6bc817e4e48026068b242b0a46df81f'>
     >>> x.lastTimeRewardApplicable()
     1658703966
     >>> chain.time()
     1658703975
     >>> 1658703966 - 1658703975
     -9
     >>> x.lastTimeRewardApplicable()
     1658703966
     >>> x.lastUpdateTime()
     1658703966
     >>> x.periodFinish()
     1659308766
     >>> 1658703966 - 1659308766
     -604800
     >>> chain.sleep(604800 // 3) ## Sleep for third of time
     >>> chain.time()
     1658905644
     >>> 1658905644- 1659308766
     -403122
     >>> x.stake(1e18, {"from": a[0]})
     Transaction sent: 0x4899faa962b45d2f746db4f045b9858fdd506185cecab019516f4b9cae4bfd37
       Gas price: 0.0 gwei   Gas limit: 12000000   Nonce: 6
       BaseRewardPool.stake confirmed   Block: 15208166   Gas used: 73201 (0.61%)
     
     <Transaction '0x4899faa962b45d2f746db4f045b9858fdd506185cecab019516f4b9cae4bfd37'>
     >>> x.balanceOf(a[0])
     1000000000000000000
     >>> x.earned(a[0])
     0
     >>> chain.sleep(x.duration())
     >>> x.earned(a[0])
     0
     >>> x.getReward(a[0], False)
     Transaction sent: 0xba12fac5aa76e59d51fa277245cd96db53d7ca2685bdf97abdee734550f102e8
       Gas price: 0.0 gwei   Gas limit: 12000000   Nonce: 7
       BaseRewardPool.getReward confirmed   Block: 15208167   Gas used: 57623 (0.48%)
     
     <Transaction '0xba12fac5aa76e59d51fa277245cd96db53d7ca2685bdf97abdee734550f102e8'>
     >>> history[-1].return_value
     666502976190414339
     >>>

Which means, that the warden has found a valid vulnerability and any time spent with a totalSupply of 0 will cause those rewards to be lost.

Because this is contingent on:

  * No deposits before adding rewards
  * Lasts only until a deposit has happened
  * Is related to loss of yield

I believe Medium Severity to be more appropriate.
