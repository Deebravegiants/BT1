# [M] Potential Reentrancy Risk In SZNSChef

## Summary
Severity: Medium
Contest weight: 0.3952
Dataset id: 13177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
// Deposit tokens to SZNSChef for reward allocation.
function deposit(uint256 _pid, uint256 _amount) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pending = ((user.amount * pool.accRewardPerShare) / 1e12) - user.rewardDebt;
        safeRewardTransfer(msg.sender, pending);
    }
    pool.token.safeTransferFrom(
        address(msg.sender),
        address(this),
        _amount
    );
    user.amount = user.amount + _amount;
    user.rewardDebt = ((user.amount * pool.accRewardPerShare) / 1e12);
    emit Deposit(msg.sender, _pid, _amount);
}
```
Note the withdraw() and emergencyWithdraw() routines in the same contract shares the same issue.

## Recommendation
Add necessary reentrancy guards to prevent unwanted reentrancy risks.
