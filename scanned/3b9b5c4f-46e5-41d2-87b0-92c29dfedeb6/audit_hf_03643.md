# [M] [WP-M1] getRewards() can be triggered by

## Summary
Severity: Medium
Contest weight: 0.1244
Dataset id: 19713
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ConvexRewardPool#getReward(address) can be called by any address besides the owner themself. The reward tokens will only be added to the assets list when getReward() is called. If there is a third party that is "helping" the account to call getReward() from time to time, by keeping the value of unclaimed rewards low, the account owner may not have the motivation to take the initiative to call getReward() via the AccountManager. As a result, the reward tokens may never get added to the account's assets list. If the helper/attacker continuously claims the rewards on behalf of the victim, the rewards will not be accounted for in the victim's total assets. As a result, the victim's account can be liquidated while actual there are enough assets in their account, it is just that these are not accounted for.

## Recommendation
Consider adding all the reward tokens to the account's assets list in ConvexBoosterController.sol#canDeposit().
