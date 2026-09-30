# [H] Improper Logic Of GymVaultsBank::_deposit()

## Summary
Severity: High
Contest weight: 0.6357
Dataset id: 12152
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the GymVaultsBank contract is one of the main entries for interaction with users. In particular, it implements an incentive mechanism that rewards the staking of supported assets with the rewardToken token. One specific entry routine, i.e., deposit(), is designed to deposit the supported assets. While examining its logic, we observe there is a vulnerability that can be exploited by the malicious actor to claim the reward repeatedly.

To elaborate, we show below the related code snippet of the GymVaultsBank contract. At the beginning of the internal _deposit() routine (which is called inside the deposit() routine), the _claim() routine is invoked (line 433) to calculate and transfer the pending rewards to msg.sender. Additionally, we notice the _claim() routine is not in charge of user.rewardDebt update. That is to say, the user.rewardDebt should be updated outside the _claim() routine. After further analysis, we notice the user.rewardDebt is updated (line 456) only when the deposit amount is larger than 0 (line 436). With that, a malicious actor can claim the reward repeatedly by making the deposit amount 0. Given this, we suggest to update the user.rewardDebt regardless the actual deposit amount.

```solidity
function deposit(
    uint256 _pid,
    uint256 _wantAmt,
    uint256 _referrerId
) external payable nonReentrant onlyEmailVerified(msg.sender) {
    _deposit(_pid, _wantAmt);
    _updateLevelPoolQualification(msg.sender);
}

function _claim(uint256 _pid, address _user) private {
    PoolInfo memory pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][_user];
    uint256 pending = (user.shares * pool.accRewardPerShare) / (1e18) - (user.rewardDebt);
    if (pending > 0) {
        uint256 _distributedRewards = _distributeRewards(pending, rewardToken, _user);
        user.totalClaims += (pending - _distributedRewards);
        _safeRewardTransfer(rewardToken, _user, (pending - _distributedRewards));
        emit RewardPaid(rewardToken, _user, pending);
    }
}

function _deposit(uint256 _pid, uint256 _wantAmt) private {
    updatePool(_pid);
    PoolInfo memory pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    if (user.shares > 0) {
        _claim(_pid, msg.sender);
    }
    if (_wantAmt > 0) {
        if (msg.value == 0 && address(pool.want) != wbnbAddress) {
            // If want not WBNB
            pool.want.safeTransferFrom(address(msg.sender), address(this), _wantAmt);
            if (address(pool.want) == busdAddress) {
                user.dollarValue += (_wantAmt / 1e18);
            } else if (address(pool.want) == wbnbAddress) {
                user.dollarValue += ((_wantAmt * IGYMNETWORK(gymNetworkAddress).getBNBPrice()) / 1e18);
            }
        }
        pool.want.safeIncreaseAllowance(pool.strategy, _wantAmt);
        uint256 sharesAdded = IStrategy(poolInfo[_pid].strategy).deposit(msg.sender, _wantAmt);
        user.shares += sharesAdded;
        _updateInvestment(msg.sender);
        userInvestment[_pid][msg.sender] += _wantAmt;
    }
    user.rewardDebt = (user.shares * (pool.accRewardPerShare)) / (1e18);
    emit Deposit(msg.sender, _pid, _wantAmt);
}
```

## Recommendation
Correct the implementation of the _deposit() routine as above-mentioned.
