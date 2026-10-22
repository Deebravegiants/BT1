# [M] Denial-of-Service in getReward()

## Summary
Severity: Medium
Contest weight: 0.5798
Dataset id: 12224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Following the discussions of Section 3.3, we further examine the incentivization mechanism to encour-
age early adoption. Specifically, each option holder is eligible to claim the rewards via the getReward()
routine. The logic is rather straightforward in firstly determining the reward amount, next marking
the option's reward-claiming status, then ensuring the rewarded amount still falls within the daily
rewarding limit, and finally transferring the reward.
Our analysis shows that the above logic does not validate the given optionID. Because of that,
a malicious actor may submit a getReward() request with an optionID that has not been created yet
(but is expected to be created soon). Considering the current algorithm for optionID assignment,
any one can reliably guess the next optionID to be created. Consequently, the owner of new optionID
will be unable to receive the reward.
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
Apply necessary sanity checks in getReward() to prevent invalid options from
claiming rewards. An example revision is shown in the following:
```solidity
function getReward(uint optionId) external {
    uint amount = rewardAmount(optionId);
    uint today = block.timestamp / 1 days;
    (IHegicOptions.State state, address holder,) = hegicOptions.options(optionId);
    require(state == IHegicOptions.State.Inactive, "The option is inactive");
    require(!rewardedOptions[optionId], "The option was rewarded");
    require(amount.add(dailyReward[today]) < MAX_DAILY_REWARD, "Exceeds daily limits");
    rewardedOptions[optionId] = true;
    dailyReward[today] = dailyReward[today].add(amount);
    hegic.safeTransfer(holder, amount);
}
```
