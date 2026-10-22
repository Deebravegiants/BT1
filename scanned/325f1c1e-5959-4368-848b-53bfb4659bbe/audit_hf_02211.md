# [M] Bypass of Daily Reward Limit in HegicRewards

## Summary
Severity: Medium
Contest weight: 0.5784
Dataset id: 12227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hegic provides an incentivization mechanism to encourage early adoption. Specifically, certain HEGIC
tokens will be distributed pro-rata on a daily basis among options holders. The logic has been
implemented in the HegicRewards contract. The current implementation sets the maximum daily
reward as MAX_DAILY_REWARD = 165_000e18.
Each option holder is eligible to claim the rewards via the getReward() routine. The logic is rather
straightforward in firstly determining the reward amount, next marking the option's reward-claiming
status, then ensuring the rewarded amount still falls within the daily rewarding limit, and finally
transferring the reward.
Our analysis shows that the above logic forgets to update the daily rewarded amount that has
been claimed so far. Therefore, the above checking of daily rewarding limit translates into that each
individual option reward is no more than the daily limit.
```solidity
function getReward(uint optionId) external {
    uint amount = rewardAmount(optionId);
    uint today = block.timestamp / 1 days;
    (,
    address holder,
    ) = hegicOptions.options(optionId);
    require(!rewardedOptions[optionId], "The option was rewarded");
    require(amount.add(dailyReward[today]) < MAX_DAILY_REWARD, "Exceeds daily limits");
    rewardedOptions[optionId] = true;
    hegic.safeTransfer(holder, amount);
}
```

## Recommendation
Revise the logic to properly implement the daily reward limit. An example
revision is shown below:
```solidity
function getReward(uint optionId) external {
    uint amount = rewardAmount(optionId);
    uint today = block.timestamp / 1 days;
    (,
    address holder,
    ) = hegicOptions.options(optionId);
    require(!rewardedOptions[optionId], "The option was rewarded");
    require(amount.add(dailyReward[today]) < MAX_DAILY_REWARD, "Exceeds daily limits");
    rewardedOptions[optionId] = true;
    dailyReward[today] = dailyReward[today].add(amount);
    hegic.safeTransfer(holder, amount);
}
```
