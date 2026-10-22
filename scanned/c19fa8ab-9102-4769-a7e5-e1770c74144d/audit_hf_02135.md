# [M] Incorrect Withdrawal Schedule Cleanup in EigenpieWithdrawManager

## Summary
Severity: Medium
Contest weight: 0.4395
Dataset id: 11980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Eigenpie protocol builds a Liquid Restaking solution that oﬀers liquidity to illiquid assets deposited into restaking platforms. While examining existing logic to withdraw previous stakes, we notice it has an incorrect implementation when clearing withdrawal schedule. In the following, we show below the related _cleanUpWithdrawalSchedules() implementation. It has a rather straightforward logic in having two for-loops to iterate current withdrawal schedules and clear previous ones. The ﬁrst for-loop iterates the given asset list and the second for-loop evaluates previous withdrawal schedules. However, it comes to our attention that the adjustment of previous schedules makes use of the wrong index claimedWithdrawalSchedules[j] (line 313), which should be claimedWithdrawalSchedules[i].
```solidity
function _cleanUpWithdrawalSchedules(address[] memory assets, uint256[] memory claimedWithdrawalSchedules) internal {
    for (uint256 i = 0; i < assets.length;) {
        bytes32 userToAsset = userToAssetKey(msg.sender, assets[i]);
        UserWithdrawalSchedule[] storage schedules = withdrawalSchedules[userToAsset];
        if (claimedWithdrawalSchedules[i] >= withdrawalscheduleCleanUp) {
            for (uint256 j = 0; j < schedules.length - claimedWithdrawalSchedules[i];) {
                schedules[j] = schedules[j + claimedWithdrawalSchedules[j]];
                unchecked {++j;}
            }
        }
        while (claimedWithdrawalSchedules[i] > 0) {
            schedules.pop();
            claimedWithdrawalSchedules[i]--;
        }
        unchecked {++i;}
    }
}
```

## Recommendation
Improve the staking logic to ensure the given minRec restriction is honored.
