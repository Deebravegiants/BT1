# [M] TRH-4 | Rewards During A Pause For A Reward Token Can Be Accrued

## Summary
Severity: Medium
Contest weight: 0.0739
Dataset id: 19567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Paused tokens are not differentiated from when calling accrue() on them. This allows a user to accrue them even though they should not be by calling claim(). This then allows users to claim yield for a token that is currently on pause. Furthermore, tokens paused through disableRewardToken() do not get accrued when calling accrue(). This would effectively lose users yield.

## Recommendation
Consider having a check for if a token is paused or not in accrue(TokenReward storage tokenReward) and returning early if it is. Also consider accruing paused tokens up until the pause point in order for all users to be able to claim them.
