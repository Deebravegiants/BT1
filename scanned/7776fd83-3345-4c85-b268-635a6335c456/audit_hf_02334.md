# [M] Proper Withdrawal Logic in Farming

## Summary
Severity: Medium
Contest weight: 0.4363
Dataset id: 12686
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Pandora protocol has a unique incentivize mechanism that aims to engage trading and farming users. While reviewing the current farming logic, we notice an important user-facing function needs to be improved.
In the following, we use the related withdrawAll() function. This function allows the user to withdraw all previously deposited funds from the farming contract. However, it comes to our attention that the given amount to the actual withdraw function withdraw() is 0 with the purpose of withdrawing all current deposits. A further examination on the withdraw() function shows the given 0 amount does not be interpreted as the full withdrawal! The inconsistency may bring unnecessary confusion to farming users and therefore needs to be resolved.
```solidity
function withdrawAll(address to) public {
    for (uint256 i = 0; i < poolInfo.length; i++) {
        withdraw(i, 0, to);
    }
}
function withdraw(uint256 pid, uint256 amount, address to) public {
    PoolInfo memory pool = updatePool(pid);
    UserInfo storage user = userInfo[pid][msg.sender];
    // Effects
    user.rewardDebt = user.rewardDebt.sub(int256(amount.mul(pool.accRewardPerShare) / ACC_PAN_PRECISION));
    user.amount = user.amount.sub(amount);
    // Interactions
    IRewarder _rewarder = rewarder[pid];
    if (address(_rewarder) != address(0)) {
        _rewarder.onReward(pid, msg.sender, to, 0, user.amount);
    }
    lpToken[pid].safeTransfer(to, amount);
    emit Withdraw(msg.sender, pid, amount, to);
}
```

## Recommendation
Revise the inconsistency between withdraw() and withdrawAll() functions in performing a full withdrawal.
