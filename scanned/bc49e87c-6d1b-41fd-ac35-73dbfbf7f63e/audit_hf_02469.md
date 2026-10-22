# [M] Reward Loss With Zero-Withdrawal In harvestAndWithdraw()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 13228
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, participating users in the PlanetFarm pool are supposed to claim their rewards via harvest()/harvestAndWithdraw(), not via withdraw(). In this section, we further examine the harvestAndWithdraw() routine. To elaborate, we show below the implementation of harvestAndWithdraw(). This routine implements a rather straightforward logic in firstly validating the given _amount for withdrawal, next computing the accumulated rewardAmount, and finally transferring the proper amount back to users.
```solidity
function harvestAndWithdraw(uint256 _amount) public nonReentrant checkPayToEntry {
UserInfo storage user = userInfo[msg.sender];
uint256 lpSupply = lpToken.balanceOf(address(this));
int maxProgressive) = config.getProgressive();
require(getBlockPass() <= config.getActivateAtBlock());
require((progressive == maxProgressive) && (lpSupply != 0), "Must have lpSupply and reach maxProgressive harvest");
require(user.amount >= _amount, "No lpToken cannot withdraw");
uint256 rewardAmount = getUserReward(msg.sender);
uint256 _harvestFee = config.getTestaFee(rewardAmount);
require(IERC20(testa).balanceOf(address(msg.sender)) > _harvestFee, "Must have enought testa before harvest");
(bool success,) = testa.call(abi.encodeWithSignature("transferFrom(address,address,uint256)", msg.sender, config.getCompany(), _harvestFee));
require(success);
if (_amount > 0)
user.amount = user.amount.sub(_amount);
removeReward(msg.sender, rewardAmount);
lpToken.safeTransfer(address(msg.sender), _amount);
jETHToken.safeTransfer(address(msg.sender), _amount);
totalStake = totalStake.sub(_amount);
SafeToken.safeTransferETH(msg.sender, rewardAmount);
emit HarvestAndWithdraw(msg.sender, _amount);
Public
```
Note that for a user to collect the rewards, the user is supposed to certain _harvestFee to the configured destination, i.e., config.getCompany() (line 1028). However, if the given amount=0, the user pays the _harvestFee, but does not get the rewardAmount. Next time, the user needs to pay the _harvestFee again! The logic is incorrect and needs to be revised to always transfer the rewardAmount no matter whatever the given amount is.

## Recommendation
Correct the logic in always rewarding the user in the harvestAndWithdraw() routine..
