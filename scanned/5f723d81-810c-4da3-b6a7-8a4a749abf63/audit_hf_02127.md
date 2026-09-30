# [H] Potential Fund Lockup For Contract Users

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 11943
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the DepositPool::deposit() routine records the depositor's balance when
funds are transferred in and the DepositPool::withdraw() routine allows the user to redeem the asset
by checking the user's balance. To elaborate, we show below the related routines.
```solidity
function deposit(uint256 _pid, uint256 _amount) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pendingAmount = user.amount.mul(pool.accRewardPerShare).div(1e12).sub(user.rewardDebt);
        if (pendingAmount > 0) {
            safeRewardTokenTransfer(msg.sender, pendingAmount);
            user.accRewardAmount = user.accRewardAmount.add(pendingAmount);
            pool.allocRewardAmount = pool.allocRewardAmount.sub(pendingAmount);
        }
    }
    if (_amount > 0) {
        ERC20(pool.token).safeTransferFrom(msg.sender, address(this), _amount);
        user.amount = user.amount.add(_amount);
        pool.totalAmount = pool.totalAmount.add(_amount);
        user.rewardDebt = user.amount.mul(pool.accRewardPerShare).div(1e12);
    }
    emit Deposit(msg.sender, _pid, _amount);
}

function withdraw(uint256 _pid, uint256 _amount) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][tx.origin];
    require(user.amount >= _amount, "DepositPool: withdraw: not good");
    updatePool(_pid);
    uint256 pendingAmount = user.amount.mul(pool.accRewardPerShare).div(1e12).sub(user.rewardDebt);
    if (pendingAmount > 0) {
        safeRewardTokenTransfer(tx.origin, pendingAmount);
        user.accRewardAmount = user.accRewardAmount.add(pendingAmount);
        pool.allocRewardAmount = pool.allocRewardAmount.sub(pendingAmount);
    }
    if (_amount > 0) {
        user.amount = user.amount.sub(_amount);
        pool.totalAmount = pool.totalAmount.sub(_amount);
        ERC20(pool.token).safeTransfer(tx.origin, _amount);
        user.rewardDebt = user.amount.mul(pool.accRewardPerShare).div(1e12);
    }
    emit Withdraw(tx.origin, _pid, _amount);
}
```
We notice the deposit() routine is using msg.sender to record the depositor balance (line 202)
while the withdraw() routine is using tx.origin to query the depositor's balance (line 244). These
two descriptors, msg.sender and tx.origin will give the same result if an EOA is calling the deposit()
routine directly. However, the values of msg.sender and tx.origin would be different when the calling
is from a contract. Thus, the funds deposited by a contract cannot be withdrawn.
Note that other routines Erc20EarnNftPool::stake()/Erc20EarnNftPool::harvest(), MysteryBox::buy()/MysteryBox::openbox(), and TradingPool::swap()/TradingPool::withdraw() share the same issue.

## Recommendation
Keep consistent of user balance descriptors to avoid failing of withdrawn
from contract user.
