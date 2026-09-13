# [M] Changes of `questRewardsPerPeriod` didn't reflected on LootCreator's `totalQuestPeriodRewards`

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-09
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/23
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0x1de5f407fb21dfc63174477f97bda560b81e2d1efd531860f53b6fcb4ee5c3a4
**Severity:** medium

**Description:**
**Description**

`totalQuestPeriodRewards` value in `LootCreator` is one of important variable to determine Quest allocation and rewardRatio on Loot creation. The `totalQuestPeriodRewards` value is assigned only via `notifyDistributedQuestPeriod`, which is called from `MultiMerkleDistributorV2` on `updateQuestPeriod` function.

```js
File: LootCreator.sol
279:     /**
280:     * @notice Notifies of a Quest period distribution
281:     * @dev Notofies of the amount distributed on a Quest for a period & allocates the budget for a gauge if needed
285:     */
286:     function notifyDistributedQuestPeriod(uint256 questId, uint256 period, uint256 totalRewards) external onlyAllowedDistributor nonReentrant {
...
295:         // If not set yet, set the total rewards for the quest & period
296: @>      if(!totalQuestPeriodSet[msg.sender][questId][period]) {
297:             totalQuestPeriodRewards[msg.sender][questId][period] = totalRewards;
298:             totalQuestPeriodSet[msg.sender][questId][period] = true;
299:         }

File: MultiMerkleDistributorV2.sol
359:     function updateQuestPeriod(uint256 questID, uint256 period, uint256 totalAmount, bytes32 merkleRoot) external onlyAllowed returns(bool) {
...
370:         if(totalAmount != questRewardsPerPeriod[questID][period]) revert Errors.IncorrectRewardAmount();
...
375:         // If a Loot Creator is set, notify it of the new Quest Period distributed
376:         if(lootCreator != address(0)) {
377: @>          ILootCreator(lootCreator).notifyDistributedQuestPeriod(questID, period, totalAmount);
378:         }
```

As we can see above, Line #296 will prevent any update of `totalQuestPeriodRewards`. So, it can only be set once.

Meanwhile, in `MultiMerkleDistributorV2` line 377, the `totalAmount` passed is equal to `questRewardsPerPeriod`.

The issue here is, this `questRewardsPerPeriod` can be updated on `fixQuestPeriod` and `emergencyUpdateQuestPeriod`. When the `questRewardsPerPeriod` changed it didn't notify LootCreator that the `totalAmount` is updated. If this issue is not fixed it will affect Loot calculation and Quest allocation in `LootCreator`.

**Attack Scenario**

The issue happen when there is changes in `questRewardsPerPeriod` after distributor notify LootCreator. Thus, LootCreator is using stale un-updated value, affecting Quest allocation and Loot creation

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

**Recommendation**

Consider to implement additional notify function which triggered on `LootCreator` from `fixQuestPeriod` and `emergencyUpdateQuestPeriod` to update `totalQuestPeriodRewards` for the certain `questId` and `period`
