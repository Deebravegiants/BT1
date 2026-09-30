# [M] Improved Logic In MainPlayPadContract::withdrawPoolRemainder()

## Summary
Severity: Medium
Contest weight: 0.4082
Dataset id: 12755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function withdrawPoolRemainder() external onlyApprover nonReentrant {
    updatePool();
    uint256 pending =
        allStakedAmount.mul(accTokensPerShare).div(1e18).sub(allRewardDebt);
    uint256 returnAmount = poolTokenAmount.sub(allPaidReward).sub(pending);
    allPaidReward = allPaidReward.add(returnAmount);
    rewardToken.safeTransfer(msg.sender, returnAmount);
    emit WithdrawPoolRemainder(msg.sender, returnAmount);
}
```
The MainPlayPadContract contract provides a privileged function for the contract approver to withdraw the remaining rewardToken from the staking pool. While examining the withdrawPoolRemainder routine of the MainPlayPadContract contract, we notice the current implementation logic can be improved. To elaborate, we show below its code snippet. It comes to our attention that this routine can be called by the contract approver at any time. If this routine is called by the approver before finishBlock, the stakers may receive less rewards than they deserve.

## Recommendation
Only allow the contract approver to call withdrawPoolRemainder when block.number > finishBlock.
