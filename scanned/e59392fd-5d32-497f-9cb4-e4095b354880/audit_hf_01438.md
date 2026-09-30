# [C] Drained contract if holder fees were non zero and are zero now due to early return

## Summary
Severity: Critical
Contest weight: 0.1894
Dataset id: 7456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_updateSharesReward() does an early return if the newRewards are 0. newRewards might be 0, but a user may still increase its shares balance, but due to the early return, its holderSharesReward[spaceId][holder].rewardPerSharePaid will not be updated. Thus, if a user had pending rewards to claim but the owner set holderFeePercent to 0, it could increase its balance by calling buyShares() without updating the pending rewards due to 0 newRewards, then claim rewards, getting much more in return and then selling the shares. Increase the amount bought in the poc to verify how the fees claimed via withdrawRewards() increase (when they should not as holder fees were set to 0).

## Recommendation
_updateSharesReward() should skip the rewardPerShareStored update if newReward is 0, but it should never skip _updateHolderReward(), as this must be called whenever a user changes its shares balance (before the change).
