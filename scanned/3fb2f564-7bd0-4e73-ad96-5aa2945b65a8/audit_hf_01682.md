# [M] in notifyRewardAmount

## Summary
Severity: Medium
Contest weight: 0.6503
Dataset id: 9160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function `notifyRewardAmount()` calculates `rewardRate` for reward token/s in `VE3DRewardPool` and `BaseRewardPool`. to calculate `rewardRate` it divides `reward` amount to `duration` but because of the rounding error in division, some of `reward` amount wouldn’t get distributed and stuck in contract (`rewardRate * duration < reward`). and contract don’t redistributes them or don’t have any mechanism to recover them. This bug can be more damaging if the precision of `rewardToken` is low or token price is high.

## Proof of Concept
This is `notifyRewardAmount()` code in `BaseRewardPool`: (contract `VE3DRewardPool` is similar)

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

As you can see it sets `rewardRate = reward.div(duration);` and this is where the rounding error happens. and even if contract distributes all in all the duration it will distribute `rewardRate * duration` which can be lower than `reward` and the extra reward amount will stuck in contract. This is `queueNewRewards()` code which calls `notifyRewardAmount()`:

```solidity
function queueNewRewards(uint256 _rewards) external returns (bool) {
    require(msg.sender == operator, "!authorized");

    _rewards = _rewards.add(queuedRewards);

    if (block.timestamp >= periodFinish) {
        notifyRewardAmount(_rewards);
        queuedRewards = 0;
        return true;
    }

    //et = now - (finish-duration)
    uint256 elapsedTime = block.timestamp.sub(periodFinish.sub(duration));
    //current at now: rewardRate * elapsedTime
    uint256 currentAtNow = rewardRate * elapsedTime;
    uint256 queuedRatio = currentAtNow.mul(1000).div(_rewards);

    //uint256 queuedRatio = currentRewards.mul(1000).div(_rewards);
    if (queuedRatio < newRewardRatio) {
        notifyRewardAmount(_rewards);
        queuedRewards = 0;
    } else {
        queuedRewards = _rewards;
    }
    return true;
}
```

As you can see it queues `rewardToken` and when the reward amount reach some point it calls `notifyRewardAmount()` and set `queuedRewards` to `0x0`. `notifyRewardAmount()` will set `rewardRate` based on `reward amount` but because of the rounding error some of the reward token `0 =< unused < duration` will stuck in contract and pool will not distribute it. if the token has low precision or has higher price then this amount value can be very big because `notifyRewardAmount()` can be called multiple times.

## Recommendation
add extra amount to `queuedRewards` so it would be distributed on next `notifyRewardAmount()` or add other mechanism to recover it.

Will be fixed by two solutions, adding precision and by adding another function. Middle risk.

The warden has shown how, due to rounding errors, `rewardRate` may round down and cause a certain amount of tokens not to be distributed.

In lack of a way for the `operator` to re-queue the undistributed rewards, those tokens will be lost.

Because we know `duration` is `604800` we can see that the `rewardRate` max loss is `604799`.

Meaning the potential max dust due to rounding down can be upwards of a number with 12 decimals  
![Screenshot 2022-07-24 at 23 38 33](https://user-images.githubusercontent.com/13383782/180666870-ce02ff32-84d5-4d8c-9dc1-cc0bf9d5ef9b.png)

Because the finding is limited to loss of Yield, I believe Medium Severity to be more appropriate.
