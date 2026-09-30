# [H] Incorrect Debt Accounting in Vault::_transferUserInfo()

## Summary
Severity: High
Contest weight: 0.6188
Dataset id: 11620
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ApeRocket protocol, there is an essential Vault contract that accepts users funds for investments through the supported strategies. To properly record the contribution from each investing user, the contract computes the share of each user by implementing itself as an ERC20-compliant token. While the share tokenization greatly facilitates the reward computation, the fact that it allows the Vault share to be transferred requires proper reward distribution.  
To elaborate, we show below the related _transferUserInfo() helper routine. This helper routine is designed to properly maintain internal accouting to keep track of each user's contribution or debt. However, our analysis shows its logic is currently flawed. In particular, the transferred amount (or share) may not be the full amount (or share) of the sender. In fact, it may only transfer a small portion of the current balance. Because of that, the internal states, i.e., reward_debt and space_debt, need to be updated accordingly with the portion, not the full amount.
```solidity
function _transferUserInfo(
    address sender,
    address recipient,
    uint256 shares
) internal {
    UserInfo storage old_user = userInfo[sender];
    UserInfo storage new_user = userInfo[recipient];
    new_user.reward_debt = new_user.reward_debt.add(old_user.reward_debt.mul(shares).div(old_user.amount));
    new_user.space_debt = new_user.space_debt.add(old_user.space_debt.mul(shares).div(old_user.amount));
    new_user.last_deposit_time = block.timestamp;
}
```
Moreover, the update of the last_deposit_time (line 340) is also problematic as it directly adds the space_debt amount with the sender's last_deposit_time!

## Recommendation
Revise the above _transferUserInfo() routine to properly maintain the internal accounting for reward and debt distribution.
