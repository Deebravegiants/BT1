# [M] Improved Logic of Vault::_withdraw()

## Summary
Severity: Medium
Contest weight: 0.5908
Dataset id: 11636
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the ApeRocket protocol allows users to invest their assets for returns.
Accordingly, it provides users a number of public functions: deposit(), withdraw(), and getRewards().
The first function invests the user funds, the second function allows the user to withdraw their funds, and the third one allows the user to claim rewards.
While examining the related functions, we notice an issue in current implementation.
To elaborate, we show below the related _claimRewards() helper that is a part of the getRewards() function.
This helper implements a rather straightforward logic in retrieving the user rewards.
However, it comes to our attention that the logic makes an implicit assumption of the contract balance is sufficient in satisfying the user withdraw request (line 297).
Unfortunately, this assumption may not always hold!
When violated, it may be of serious detriment to the normal functionality, including the user withdraws and claims of pending rewards.
```solidity
function _claimRewards(address _user) internal {
    UserInfo storage user = userInfo[_user];
    if (balanceOf(_user) > 0) {
        uint256 reward = earned(_user);
        if (reward > 0) {
            totalPendingRewards = totalPendingRewards.sub(reward);
            uint256 balance = farmedToken.balanceOf(address(this));
            if (balance < reward) {
                _withdrawRewards(balance, reward);
            }
            farmedToken.safeTransfer(_user, reward);
            user.reward_debt = balanceOf(_user).mul(accRewardPerShare).div(1e12);
        }
    }
}
```
Note this issue is applicable to both _claimRewards() and _withdraw().

## Recommendation
Revise the above _claimRewards() routine to properly take into account the scenario with an insufficient balance.
An example revision is shown as below:
```solidity
function _claimRewards(address _user) internal {
    UserInfo storage user = userInfo[_user];
    if (balanceOf(_user) > 0) {
        uint256 reward = earned(_user);
        if (reward > 0) {
            totalPendingRewards = totalPendingRewards.sub(reward);
            uint256 balance = farmedToken.balanceOf(address(this));
            if (balance < reward) {
                reward = _withdrawRewards(balance, reward);
            }
            farmedToken.safeTransfer(_user, reward);
            user.reward_debt = balanceOf(_user).mul(accRewardPerShare).div(1e12);
        }
    }
}
```
