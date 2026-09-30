# [M] `StakingRewards.sol#notifyRewardAmount

## Summary
Severity: Medium
Contest weight: 0.2849
Dataset id: 1557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[StakingRewards.sol#L154-L158](https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/StakingRewards.sol#L154-L158)  

    uint256 balance = rewardsToken.balanceOf(address(this));
    require(
        rewardRate <= balance / rewardsDuration,
        "Provided reward too high"
    );

In the current implementation, the contract only checks if balanceOf `rewardsToken` is greater than or equal to the future rewards.

However, under normal circumstances, since users can not withdraw all their rewards in time, the balance in the contract contains rewards that belong to the users but have not been withdrawn yet. This means the current checks can not be sufficient enough to make sure the contract has enough amount of rewardsToken.

As a result, if the `rewardsDistribution` mistakenly `notifyRewardAmount` with a larger amount, the contract may end up in a wrong state that makes some users unable to claim their rewards.

## Proof of Concept
Given:

  * rewardsDuration = 7 days;
  * Alice stakes `1,000` stakingToken;
  * `rewardsDistribution` sends `100` rewardsToken to the contract;
  * `rewardsDistribution` calls `notifyRewardAmount()` with `amount` = `100`;
  * 7 days later, Alice calls `earned()` and it returns `100` rewardsToken, but Alice choose not to `getReward()` for now;
  * `rewardsDistribution` calls `notifyRewardAmount()` with `amount` = `100` without send any fund to contract, the tx will succees;
  * 7 days later, Alice calls `earned()` `200` rewardsToken, when Alice tries to call `getReward()`, the transaction will fail due to insufficient balance of rewardsToken.

Expected Results:

The tx in step 5 should revert.

## Recommendation
Consider changing the function `notifyRewardAmount` to `addRward` and use `transferFrom` to transfer rewardsToken into the contract:
    
    function addRward(uint256 reward)
        external
        updateReward(address(0))
    {
        require(
            msg.sender == rewardsDistribution,
            "Caller is not RewardsDistribution contract"
        );

        if (block.timestamp >= periodFinish) {
            rewardRate = reward / rewardsDuration;
        } else {
            uint256 remaining = periodFinish - block.timestamp;
            uint256 leftover = remaining * rewardRate;
            rewardRate = (reward + leftover) / rewardsDuration;
        }

        rewardsToken.safeTransferFrom(msg.sender, address(this), reward);

        lastUpdateTime = block.timestamp;
        periodFinish = block.timestamp + rewardsDuration;
        emit RewardAdded(reward);
    }

Given the code available, the warden has shown a possible scenario where certain depositors cannot receive reward tokens.

Because this is contingent on an improper configuration and because this relates to loss of Yield, I believe Medium Severity to be more appropriate.
