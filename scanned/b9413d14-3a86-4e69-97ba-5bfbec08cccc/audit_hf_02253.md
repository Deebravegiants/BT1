# [H] Business Logic Error in _claimYearlyReward()

## Summary
Severity: High
Contest weight: 0.6279
Dataset id: 12390
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, besides weekly rewards, the Legends Never Die users can also claim yearly rewards after the auction lobby is over. When reviewing the implementation of the MasterVault contract, we notice that the _claimYearlyReward() function has a business logic error which may make users unable to get yearly rewards. As shown in the following code snippets, the internal function _claimYearlyReward() calculates the amounts of the yearly rewards for msg.sender. However, if msg.sender has claimed the weekly rewards from the latest vault which the msg.sender staked into, the value of user.claimed (lines 571) would be true and no yearly rewards can be claimed from the MasterVault contract by this msg.sender.
```solidity
function _claimYearlyReward()
    internal
    returns (uint256 returnAmount, uint256 rewardAmount)
{
    VaultInfo memory vault = vaultInfo[yearlyRewardIndex];
    StakedInfo storage userStakedInfo = stakedInfoUser[_msgSender()];
    UserInfo storage user = userInfo[userStakedInfo.lastStakeIndex][_msgSender()];
    if (vault.stop <= block.number && !userStakedInfo.yearleRewardClaimed && !user.claimed) {
        uint256 userStakedInfolyStrength = yearlyRewardIndex - userStakedInfo.startIndex + 1;
        uint256 userAmountStrength = (user.balance * 50 * 1e16) / 1e18;
        uint256 userTotalStrength = userStakedInfolyStrength * userAmountStrength;
        uint256 cummulativeTotalStrength = ((((yearlyRewardIndex + 1) * totalAmount) - totalWeight) * 50 * 1e16) / 1e18;
        returnAmount = (((vault.allTotalSupply * 50 * 1e16) / 1e18) * userTotalStrength) / cummulativeTotalStrength;
        if (vault.allTotalReward > 0) {
            rewardAmount = (((vault.allTotalReward * 50 * 1e16) / 1e18) * userTotalStrength) / cummulativeTotalStrength;
        }
        userStakedInfo.yearleRewardClaimed = true;
    }
}
```

## Recommendation
Remove && !user.claimed from the if statement (lines 571).
