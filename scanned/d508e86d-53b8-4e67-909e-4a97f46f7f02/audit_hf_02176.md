# [M] Revisited Reentrancy Protection In Current Implementation

## Summary
Severity: Medium
Contest weight: 0.4214
Dataset id: 12139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function deposit(address _token, uint256 _amount) external {
    PoolInfo storage pool = poolInfo[_token];
    require(pool.lastRewardTime > 0);
    _updateEmissions();
    _updatePool(_token, totalAllocPoint);
    UserInfo storage user = userInfo[_token][msg.sender];
    uint256 userAmount = user.amount;
    uint256 accRewardPerShare = pool.accRewardPerShare;
    if (userAmount > 0) {
        uint256 pending = userAmount.mul(accRewardPerShare).div(1e12).sub(user.rewardDebt);
        if (pending > 0) {
            userBaseClaimable[msg.sender] = userBaseClaimable[msg.sender].add(pending);
        }
    }
    IERC20(_token).safeTransferFrom(address(msg.sender), address(this), _amount);
    userAmount = userAmount.add(_amount);
    user.amount = userAmount;
    user.rewardDebt = userAmount.mul(accRewardPerShare).div(1e12);
    if (pool.onwardIncentives != IOnwardIncentivesController(0)) {
        uint256 lpSupply = IERC20(_token).balanceOf(address(this));
        pool.onwardIncentives.handleAction(_token, msg.sender, userAmount, lpSupply);
    }
    emit Deposit(_token, msg.sender, _amount);
}
```
We observe the current implementation of the MasterChef and MultiFeeDistribution contracts haven't considered reentrancy protection.

## Recommendation
Add necessary reentrancy guards to prevent unwanted reentrancy risks.
