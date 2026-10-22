# [M] Unclaimed rewards when emergency with-

## Summary
Severity: Medium
Contest weight: 0.5714
Dataset id: 23006
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unclaimed rewards when emergency withdrawing are not redistributed in MasterChef and MlumStaking.
Users can call MasterChef#emergencyWithdraw, MlumStaking#emergencyWithdraw to withdraw tokens without claiming the rewards.
But the unclaimed rewards are not redistributed in emergencyWithdraw call, which will left the rewards stuck in the contracts and lost forever. Other users can not claim the rewards and the protocol can not redistribute the rewards.
Unclaimed rewards when emergency withdrawing in MasterChef and MlumStaking will stuck in the contracts and lost forever.

## Recommendation
Redistribute the unclaimed rewards in emergencyWithdraw
MasterchefV2.sol
```solidity
function emergencyWithdraw(uint256 pid) external override {
    Farm storage farm = _farms[pid];
    uint256 balance = farm.amounts.getAmountOf(msg.sender);
    int256 deltaAmount = -balance.toInt256();
    (uint256 oldBalance, uint256 newBalance, uint256 oldTotalSupply,) =
        farm.amounts.update(msg.sender, deltaAmount);
    uint256 totalLumRewardForPid = _getRewardForPid(farm.rewarder, pid, oldTotalSupply);
    uint256 lumRewardForPid = _mintLum(totalLumRewardForPid);
    uint256 lumReward = farm.rewarder.update(msg.sender, oldBalance, newBalance, oldTotalSupply, lumRewardForPid);
    lumReward = lumReward + unclaimedRewards[pid][msg.sender];
    unclaimedRewards[pid][msg.sender] = 0;
    farm.rewarder.updateAccDebtPerShare(oldTotalSupply, lumReward);
    farm.token.safeTransfer(msg.sender, balance);
    emit PositionModified(pid, msg.sender, deltaAmount, 0);
}
```
MlumStaking.sol
```solidity
function emergencyWithdraw(uint256 tokenId) external override nonReentrant {
    _requireOnlyOwnerOf(tokenId);
    StakingPosition storage position = _stakingPositions[tokenId];
    // position should be unlocked
    require(
        _unlockOperators.contains(msg.sender)
        || (position.startLockTime + position.lockDuration) <= _currentBlockTimestamp() || isUnlocked(),
        "locked"
    );
    // emergencyWithdraw: locked
    _updatePool();
    uint256 pending = position.amountWithMultiplier * _accRewardsPerShare / PRECISION_FACTOR - position.rewardDebt;
    _lastRewardBalance = _lastRewardBalance - pending;
    uint256 amount = position.amount;
    // update total lp supply
    _stakedSupply = _stakedSupply - amount;
    _stakedSupplyWithMultiplier = _stakedSupplyWithMultiplier - position.amountWithMultiplier;
    // destroy position (ignore boost points)
    _destroyPosition(tokenId);
    emit EmergencyWithdraw(tokenId, amount);
    stakedToken.safeTransfer(msg.sender, amount);
}
```
