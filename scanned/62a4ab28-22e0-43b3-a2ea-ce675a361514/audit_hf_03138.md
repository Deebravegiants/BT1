# [M] escrowedReward will be frozen in the contract if

## Summary
Severity: Medium
Contest weight: 0.4013
Dataset id: 17625
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A portion of users' reward, which is expected to be "escrowed", will be frozen in the pool contract if escrowPool == address(0) but escrowPortion > 0.  
Setting _escrowPool to address(0) is allowed in __BasePool_init():  
ining/contracts/base/BasePool.sol#L75-L77  
However, when escrowPortion > 0, if escrowPool == address(0), claimRewards() will still only transferring nonEscrowedRewardAmount to the _receiver and left the escrowedRewardAmount in the contract.  
As a result, a portion (escrowPortion) of the rewards will be frozen in the contract, and there is no way for the users or even the admin to retrieve these rewards.

## Recommendation
Change to:  
```solidity
function claimRewards(address _receiver) external {
    uint256 rewardAmount = _prepareCollect(_msgSender());
    uint256 escrowedRewardAmount = 0;
    if (escrowPortion != 0 && address(escrowPool) != address(0)) {
        escrowedRewardAmount = rewardAmount * escrowPortion / 1e18;
        if (escrowedRewardAmount != 0) {
            escrowPool.deposit(escrowedRewardAmount, escrowDuration, _receiver);
            rewardAmount -= escrowedRewardAmount;
        }
    }
    // ignore dust
    if (rewardAmount > 1) {
        rewardToken.safeTransfer(_receiver, rewardAmount);
    }
    emit RewardsClaimed(_msgSender(), _receiver, escrowedRewardAmount, rewardAmount);
}
```
