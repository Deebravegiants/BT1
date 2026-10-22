# [H] When queueNewRewards is called, caller could

## Summary
Severity: High
Contest weight: 0.7984
Dataset id: 20309
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside queueNewRewards, irrespective of whether we're near the start or the end of a
reward period, if the accrued rewards are too large relative to the new rewards
(queuedRatio is greater than newRewardRatio), the new rewards will be added to the
queue (queuedRewards) rather than being immediately distributed.
3-07-14/src/rewarders/AbstractRewarder.sol#L235-L261
```solidity
function queueNewRewards(uint256 newRewards) external onlyWhitelisted {
    uint256 startingQueuedRewards = queuedRewards;
    uint256 startingNewRewards = newRewards;
    newRewards += startingQueuedRewards;
    if (block.number >= periodInBlockFinish) {
        notifyRewardAmount(newRewards);
        queuedRewards = 0;
    } else {
        uint256 elapsedBlock = block.number - (periodInBlockFinish - durationInBlock);
        uint256 currentAtNow = rewardRate * elapsedBlock;
        uint256 queuedRatio = currentAtNow * 1000 / newRewards;
        if (queuedRatio < newRewardRatio) {
            notifyRewardAmount(newRewards);
            queuedRewards = 0;
        } else {
            queuedRewards = newRewards;
        }
    }
    emit QueuedRewardsUpdated(startingQueuedRewards, startingNewRewards, queuedRewards);
    // Transfer the new rewards from the caller to this contract.
    IERC20(rewardToken).safeTransferFrom(msg.sender, address(this), newRewards);
}
```
However, when this function tried to pull funds from sender via safeTransferFrom, it
used newRewards amount, which already added by startingQueuedRewards. If
previously queuedRewards already have value, the processed amount will be wrong.
There are two possible issue here :
1. If previously queuedRewards is not 0, and the caller don't have enough funds or
approval, the call will revert due to this logic error.
2. If previously queuedRewards is not 0, and the caller have enough funds and
approval, the caller funds will be pulled more than it should (reward param + queuedRewards )

## Recommendation
Update the transfer to use startingNewRewards instead of newRewards :
```solidity
function queueNewRewards(uint256 newRewards) external onlyWhitelisted {
    uint256 startingQueuedRewards = queuedRewards;
    uint256 startingNewRewards = newRewards;
    newRewards += startingQueuedRewards;
    if (block.number >= periodInBlockFinish) {
        notifyRewardAmount(newRewards);
        queuedRewards = 0;
    } else {
        uint256 elapsedBlock = block.number - (periodInBlockFinish - durationInBlock);
        uint256 currentAtNow = rewardRate * elapsedBlock;
        uint256 queuedRatio = currentAtNow * 1000 / newRewards;
        if (queuedRatio < newRewardRatio) {
            notifyRewardAmount(newRewards);
            queuedRewards = 0;
        } else {
            queuedRewards = newRewards;
        }
    }
    emit QueuedRewardsUpdated(startingQueuedRewards, startingNewRewards, queuedRewards);
    // Transfer the new rewards from the caller to this contract.
    IERC20(rewardToken).safeTransferFrom(msg.sender, address(this), startingNewRewards);
}
```
