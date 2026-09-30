# [M] Proper Withdraw Fee Collection in withdraw()

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the core of FarmHero is the HeroFarmV3 contract that is developed on the widely-used MasterChef contract. Moreover, it adds the new feature of supporting NFT-based staking and unstaking. While examining the current logic, we notice the current implementation supports the collection of withdraw fee and the current fee collection logic is flawed. To elaborate, we show below the full implementation of the withdraw() function. Our analysis shows that the withdraw fee collection is contingent on the following conditions if (withdrawFee || !feeExclude[msg.sender]) (line 647). Basically, it requires two conditions: the first one is the withdrawFee is intended and the second one is that the user is not excluded. However, the current implementation collects the withdraw fee as long as one condition is satisfied. For correction, it requires both conditions to be met at the same time, i.e., if (withdrawFee && !feeExclude[msg.sender])
```solidity
// Withdraw LP tokens from MasterChef.
function withdraw(uint256 _pid, uint256 _wantAmt) public isEOA nonReentrant whenNotPaused {
    updatePool(_pid);
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    require(pool.poolType == PoolType.ERC20, "invalid erc20");
    uint256 wantLockedTotal = IStrategy(poolInfo[_pid].strat).wantLockedTotal();
    uint256 sharesTotal = IStrategy(poolInfo[_pid].strat).sharesTotal();
    require(user.shares > 0, "user.shares is 0");
    require(sharesTotal > 0, "sharesTotal is 0");

    // Withdraw pending HERO
    uint256 pending = user.shares.mul(pool.accHEROPerShare).div(1e12).sub(user.rewardDebt);
    if (pending > 0) {
        _withdrawReward(pending);
    }

    // Withdraw want tokens
    uint256 amount = user.shares.mul(wantLockedTotal).div(sharesTotal);
    if (_wantAmt > amount) {
        _wantAmt = amount;
    }
    if (_wantAmt > 0) {
        uint256 sharesRemoved = IStrategy(poolInfo[_pid].strat).withdraw(msg.sender, _wantAmt);
        if (sharesRemoved > user.shares) {
            user.shares = 0;
        } else {
            user.shares = user.shares.sub(sharesRemoved);
        }
        uint256 wantBal = IERC20(pool.want).balanceOf(address(this));
        if (wantBal < _wantAmt) {
            _wantAmt = wantBal;
        }
        if (withdrawFee || !feeExclude[msg.sender]) {
            uint256 feeRate = _calcFeeRateByGracePeriod(uint256(user.gracePeriod));
            if (feeRate > 0) {
                uint256 feeAmount = _wantAmt.mul(feeRate).div(10000);
                _wantAmt = _wantAmt.sub(feeAmount);
                IERC20(pool.want).safeTransfer(feeAddress, feeAmount);
            }
        }
        IERC20(pool.want).safeTransfer(address(msg.sender), _wantAmt);
        if (_wantAmt == 0 && rewardDistribution != address(0)) {
            IRewardDistribution(rewardDistribution).earn(address(this));
        }
    }
    user.rewardDebt = user.shares.mul(pool.accHEROPerShare).div(1e12);
    // If user withdraws all the LPs, then gracePeriod cleared
    if (user.shares == 0) {
        user.gracePeriod = 0;
    }
    emit Withdraw(msg.sender, _pid, _wantAmt);
}
```

## Recommendation
Improve the above withdraw() function by collecting the withdraw fee when (withdrawFee && !feeExclude[msg.sender]) is evaluated to be true.
