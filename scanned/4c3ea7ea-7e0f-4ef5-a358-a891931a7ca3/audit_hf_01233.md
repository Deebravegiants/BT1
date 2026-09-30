# [M] `BkdLocker#depositFees`

## Summary
Severity: Medium
Contest weight: 0.4799
Dataset id: 5628
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function depositFees(uint256 amount) external override {
    require(amount > 0, Error.INVALID_AMOUNT);
    require(totalLockedBoosted > 0, Error.NOT_ENOUGH_FUNDS);
    IERC20(rewardToken).safeTransferFrom(msg.sender, address(this), amount);

    RewardTokenData storage curRewardTokenData = rewardTokenData[rewardToken];

    curRewardTokenData.feeIntegral += amount.scaledDiv(totalLockedBoosted);
    curRewardTokenData.feeBalance += amount;
    emit FeesDeposited(amount);
}
```

Every time the `BkdLocker#depositFees()` gets called, there will be a surge of rewards per locked token for the existing stakeholders.

This enables a well-known attack vector, in which the attacker will take a large portion of the shares before the surge, then claim the rewards and exit immediately.

While the `_WITHDRAW_DELAY` can be set longer to mitigate this issue in the current implementation, it is possible for the admin to configure it to a very short period of time or even `0`.

In which case, the attack will be very practical and effectively steal the major part of the newly added rewards.

## Proof of Concept
Given:

* Current `totalLockedBoosted()` is `100,000 govToken`;
* Pending distribution fees amount is `1,000 rewardToken`;
* `depositFees()` is called to add `1,000 rewardToken`;
* The attacker frontrun the 1st transaction with a `lock()` transaction to deposit `100,000 govToken`, taking 50% of the pool;
* After the transaction in step 1 is mined, the attacker calls `claimFees()` and received `500 rewardToken`.

As a result, the attacker has stolen half of the pending fees which belong to the old users.

## Recommendation
Consider switching the reward to a `rewardRate`-based gradual release model, such as Synthetix’s StakingRewards contract.

See: <https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol#L113-L132>

The withdrawal delay prevents this attack.

Given the need for:
* Withdrawal delay set to 0 or small
* Need for front-running which causes leak of value

I believe High Severity to be out of the question.
That said, because the rewards are given out at the time of `depositFees`, and they are not linearly vested, I do believe that a front-run MEV attack can be executed, being able to immediately claim the reward tokens, at the cost / risk of having to lock the tokens.
The shorter the withdrawal delay, the lower the risk for the attack..
Because this is contingent on configuration, and at best it’s a loss of yield for the lockers, I believe Medium Severity to be more appropriat.

As an additional note, please consider the fact that if the potential value gained is high enough, an attacker could just hedge the risk of locking by shorting the tokens, effectively being delta neutral while using the rewards for profit.
This means that if your token becomes liquid enough (a goal for any protocol), you would expect the withdrawal delay to become ineffective as hedging options become available.
Forcing the rewards to linearly vest will prevent the front-run from being effective and will reward long term lockers.
