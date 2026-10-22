# [M] Improved Deletion Logic In Bottle::withdraw()

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 11698
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BabySwap protocol, the Bottle contract provides incentive mechanisms that reward the voting of supported _voteId with certain reward tokens. It allows the user to start a pool and vote for the supporting _voteId by adding funds during the pool's voting schedule. While reviewing the implementation of the pool deletion logic, we notice the new pool may fail to be created because of the wrongly deleted old pool. To elaborate, we show below the withdraw() function in the Bottle contract.
```solidity
function withdraw(uint256 _voteId, address _for) external nonReentrant {
    createPool();
    // require( currentVoteId <= 4 || _voteId >= currentVoteId - 4, "illegal voteId ");
    PoolInfo memory _pool = poolInfo[_voteId];
    require(_pool.avaliable, "illegal voteId");
    require(block.timestamp > _pool.unlockAt, "not the right time");
    UserInfo memory _userInfo = userInfo[_voteId][msg.sender][_for];
    require(_userInfo.amount > 0, "illegal amount");
    // uint _pending = masterChef.pendingCake(0, address(this));
    uint256 balanceBefore = babyToken.balanceOf(address(this));
    masterChef.leaveStaking(0);
    uint256 balanceAfter = babyToken.balanceOf(address(this));
    uint256 _pending = balanceAfter.sub(balanceBefore);
    uint _totalShares = totalShares;
    if (_pending > 0 && _totalShares > 0) {
        accBabyPerShare = accBabyPerShare.add(_pending.mul(RATIO).div(_totalShares));
    }
    uint _userPending = _userInfo.pending.add(_userInfo.amount.mul(accBabyPerShare).div(RATIO).sub(_userInfo.rewardDebt));
    uint _totalPending = _userPending.add(_userInfo.amount);
    if (_totalPending >= _pending) {
        masterChef.leaveStaking(_totalPending.sub(_pending));
    } else {
        // masterChef.leaveStaking(0);
        babyToken.approve(address(masterChef), _pending.sub(_totalPending));
        masterChef.enterStaking(_pending.sub(_totalPending));
    }
    //if (_totalPending > 0) {
    SafeBEP20.safeTransfer(babyToken, msg.sender, _totalPending);
    if (_userPending > 0) {
        emit Claim(_voteId, msg.sender, _for, _userPending);
    }
    totalShares = _totalShares.sub(_userInfo.amount);
    poolInfo[_voteId].totalAmount = _pool.totalAmount.sub(_userInfo.amount);
    delete userInfo[_voteId][msg.sender][_for];
    if (poolInfo[_voteId].totalAmount == 0) {
        delete poolInfo[_voteId];
        emit DeleteVote(_voteId);
    }
    emit Withdraw(_voteId, msg.sender, _for, _userInfo.amount);
}
```
The deletion of the current pool, i.e., delete userInfo[_voteId][msg.sender][_for] (line 198), may be performed when block.timestamp < _currentPool.finishAt. In other words, the old pool may be deleted before a new pool created. In this case, _currentPool.finishAt will give a 0 value and the new created pool's voting schedule is invalid.

## Recommendation
Improve the pool deletion logic in Bottle::withdraw().
