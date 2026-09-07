# [M] Reward calculation is incorrect

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-28
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/49
Type: hats-finding

## Details
**Github username:** @8ahoz
**Submission hash (on-chain):** 0x9c755d2f8bba921b6311df35afcfcd314adf98a3eebec6aa273d59a2a7c718c7
**Severity:** medium severity

**Description:**
### Reward calculation is incorrect

`configureRewards()` in DistributionManager.sol can be called by `EMISSION_MANAGER` to create a new incentivizedAsset with reward config. This function first checks `_incentivizedAssets` mapping and if the incentivized asset does not exist there it pushes the asset to the `_allIncentivizedAssets` array. Then it does a similar thing for reward asset, however this time check happens in `incentivizedAsset.rewardData` which means the function checks if the `rewardData` exists for that specific `incentivizedAsset` and if that specific reward address is not set for that specific incentivized asset index, the reward token gets pushed to the `_allRewards` array which is global for all incentivized assets.

The issue described above will cause the same reward data to be pushed to the array more than once if it is used as a reward to multiple incentivized assets. By checking `IncentivesController:claimReward()` we can understand the protocol plans to use the same reward token for multiple assets which means the double accounting of reward tokens in `_allRewards` is inevitable.

`IncentivesController:getPendingRewards()` iterates through all assets for a user, and for each asset it iterates over each reward in `_allRewards` array. As explained above, rewards will be saved in this array more than once which will cause reward to be accounted multiple times for the same asset and same reward. Causing returned reward amount to be multiplied by the times the reward token is used in the protocol. 

A similar issue exists for `IncentivesController:claimAllRewards()` Here again, the same reward is accounted multiple times but thanks to the following line, subsequent accountings will return only 0 extra reward to the claimer, preventing a critical vulnerability but still causing all claimers to overpay for gas for each time the reward token is used.
https://github.com/VMEX-finance/vmex/blob/68e969e252d7fb501e308c230dbba0967965c9f3/packages/contracts/contracts/protocol/incentives/IncentivesController.sol#L217

**PoC:**

- `EMISSION_MANAGER` calls configureReward for assetA with reward tokenX
- `EMISSION_MANAGER` calls configureReward for assetB with reward tokenX
- `EMISSION_MANAGER` calls configureReward for assetC with reward tokenX
- Since tokenX is pushed to the `_allRewards` 3 times, `getPendingRewards()` returns 3x rewards for every user
- `claimAllRewards()` also calculates rewards for each asset 3 times, making it more costly

**Recommendation:**

`configureRewards()` should not push the same reward token to `_allRewards` more than once. Keep a mapping for already added reward tokens, and only push to array if the token is not in the mapping.
