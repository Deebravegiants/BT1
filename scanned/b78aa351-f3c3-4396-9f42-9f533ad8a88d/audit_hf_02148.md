# [M] Incorrect Reward Calculation in ATokenRewardsReDistributionManager

## Summary
Severity: Medium
Contest weight: 0.4402
Dataset id: 12039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Extra Finance protocol brings in new staking component and enhanced debt payment. The new staking component is incentivized with extra reward distribution. While examining the associated incentive mechanism, we notice current approach to calculate reward amount should be revisited.

To elaborate, we show below the implementation of the related getUnderlyigRewards() routine. As the name indicates, this routine is used to query underlying rewards. It comes to our attention that the internal variable of accumulatedRewardsIndex is properly scaled by PRECISION (line 58). However, the calculated user reward amount is not properly scaled back (line 61). Note another routine _claimUnderlyingRewards() shares the same issue.

```solidity
function getUnderlyigRewards(
    address user
) external view returns (address[] memory, uint256[] memory) {
    (address[] memory rewardsList, uint256[] memory underlyingUnclaimedAmounts) = _getAllPendingRewards();
    require(rewardsList.length == underlyingUnclaimedAmounts.length);
    uint256[] memory unclaimedAmounts = new uint256[](rewardsList.length);
    uint256 total = totalShares();
    uint256 share = userShares(user);
    for (uint i = 0; i < rewardsList.length; ++i) {
        if (total > 0 && underlyingUnclaimedAmounts[i] > 0) {
            uint256 accumulatedRewardsIndex = rewardsData[rewardsList[i]].accumulatedRewardsIndex + (PRECISION * underlyingUnclaimedAmounts[i]) / total;
            unclaimedAmounts[i] = (accumulatedRewardsIndex - userRewardsIndex[user]) * share;
        }
    }
    return (rewardsList, unclaimedAmounts);
}
```

## Recommendation
Consider the removal of the redundant state (or code) with a simpliﬁed, consistent implementation.
