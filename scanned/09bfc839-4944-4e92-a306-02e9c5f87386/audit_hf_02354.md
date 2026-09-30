# [M] Improved Logic In MainPlayPadContract::stakeTokens()

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
// stake tokens with controls
function stakeTokens(uint256 _amountToStake) external nonReentrant {
    updatePool();
    uint256 pending = 0;
    uint256 randomPoolId =
        uint256(
            keccak256(
                abi.encodePacked(
                    msg.sender,
                    now,
                    block.number,
                    _amountToStake
                )
            )
        );
    require(!availablePools[randomPoolId], "Pool id already created");
    UserInfo storage user = userInfo[msg.sender];
    UserPoolInfo storage poolInfo = userPoolInfo[randomPoolId];
    if (user.amount > 0) {
        pending = transferPendingReward(user);
    } else if (_amountToStake > 0) {
        participants += 1;
    }
    if (_amountToStake > 0) {
        stakingToken.safeTransferFrom(
            msg.sender,
            address(this),
            _amountToStake
        );
    }
    if(user.userAddress == address(0x0000000000000000000000000000000000000000)){
        allInvestors.push(msg.sender);
    }
    availablePools[randomPoolId] = true;
    poolInfo.blockNumber = block.number;
    poolInfo.amount = _amountToStake;
    poolInfo.owner = msg.sender;
    poolInfo.penaltyEndBlockNumber = block.number.add(penaltyBlockLength);
    if(user.amount.add(_amountToStake) > limitForPrize ){
        user.onlyPrize = false;
        user.stakeStartDate = block.timestamp;
    }else{
        user.onlyPrize = true;
    }
    user.stakeStatus = true;
    user.userAddress = msg.sender;
    user.userPoolIds.push(randomPoolId);
    user.amount = user.amount.add(_amountToStake);
    allStakedAmount = allStakedAmount.add(_amountToStake);
    allRewardDebt = allRewardDebt.sub(user.rewardDebt);
    user.rewardDebt = user.amount.mul(accTokensPerShare).div(1e18);
    allRewardDebt = allRewardDebt.add(user.rewardDebt);
    emit TokensStaked(msg.sender, _amountToStake, pending);
}
```
The PlayPad-IDO-DQ protocol users can stake their stakingToken to the MainPlayPadContract contract to earn rewards. While examining the stakeTokens() routine of the MainPlayPadContract contract, we notice the current implementation logic can be improved. To elaborate, we show below its code snippet. It comes to our attention that when staking stakingToken to MainPlayPadContract, the user.stakeStartDate state will be updated every time if the total staked amount of a staker is above the limit for vesting, i.e., limitForPrize (lines 1074). However, the user.stakeStartDate of the staker should only be updated when the total staked amount of this staker is above the vesting limit for the first time.

## Recommendation
Update the user.stakeStartDate for a staker only when the total staked amount of this staker is above the vesting limit for the first time.
