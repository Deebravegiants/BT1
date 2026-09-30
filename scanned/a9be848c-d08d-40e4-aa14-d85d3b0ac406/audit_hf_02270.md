# [M] Oversized Rewards May Lock All Pool Stakes

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 12440
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In this section, we continue to examine the FeeSharingSystem logic and focus on the _rewardPerToken() routine. This routine is responsible for calculating the reward rate for each staked token.
Our analysis leads to the discovery of a potential pitfall when a new oversized reward amount is added into the pool. In particular, as the _rewardPerToken() routine involves the multiplication of three uint256 integer, it is possible for their multiplication to have an undesirable overflow (lines 279-280), especially when the currentRewardPerBlock is largely controlled by an external entity (through the updateRewards() function).
```solidity
function updateRewards(uint256 reward, uint256 rewardDurationInBlocks) external onlyOwner {
    // Adjust the current reward per block
    if (block.number >= periodEndBlock) {
        currentRewardPerBlock = reward / rewardDurationInBlocks;
    } else {
        currentRewardPerBlock =
            (reward + ((periodEndBlock - block.number) * currentRewardPerBlock)) /
            rewardDurationInBlocks;
    }
    lastUpdateBlock = block.number;
    periodEndBlock = block.number + rewardDurationInBlocks;
    emit NewRewardPeriod(rewardDurationInBlocks, currentRewardPerBlock, reward);
}
function _rewardPerToken() internal view returns (uint256) {
    if (totalShares == 0) return rewardPerTokenStored;
    return
        rewardPerTokenStored +
        ((_lastRewardBlock() - lastUpdateBlock) * (currentRewardPerBlock * PRECISION_FACTOR)) /
        totalShares;
}
```
This issue is made possible if the reward amount is given as the argument to updateRewards() such that the calculation of currentRewardPerBlock.mul(1e18) always overflows, hence locking all deposited funds. Note that an authentication check on the caller of updateRewards() greatly alleviates such concern. Currently, only the owner address is able to call updateRewards(). Apparently, if the owner is a normal address, it may put users funds at risk. To mitigate this issue, it is important to transfer the ownership to the governance and ensure the given reward amount will not be oversized to overflow and lock users funds.

## Recommendation
Ensure the reward amount is appropriate, without resulting in overflowing and locking users funds.
