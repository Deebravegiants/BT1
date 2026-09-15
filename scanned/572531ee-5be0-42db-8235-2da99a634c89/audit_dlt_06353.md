# [M] Division by Zero in `_createLoot` when Distributor change `lootCreator`, prevent Users from creating previous Loot

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-14
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/56
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0xf76a45fdb970b1ed33632ae8bc5fc774dde360cd36d4dae75db5e4dbc02ad4b2
**Severity:** medium

**Description:**
**Description**

The `lootCreator` in `MultiMerkleDistributorV2` can be changed via `setLootCreator`. If the `lootCreator` can only be set once, then the function should be

```diff
File: MultiMerkleDistributorV2.sol
393:     function setLootCreator(address _lootCreator) external onlyOwner {
++           if(lootCreator != address(0)) revert Errors.LootCreatorAlreadySetted();
394:         address oldCreator = lootCreator;
395:         lootCreator = _lootCreator;
396: 
397:         emit LootCreatorUpdated(oldCreator, _lootCreator);
398:     }
```

but since the check above is not exist, I assume the LootCreator can be changed even after the first initialization.

By design, the `claim` in Distributor is not restricted only callable for the current running period, user can `claim` for late period, for example if the current period is week 10, they can claim from period week 5 if they have reward on it.

```js
File: MultiMerkleDistributorV2.sol
359:     function updateQuestPeriod(uint256 questID, uint256 period, uint256 totalAmount, bytes32 merkleRoot) external onlyAllowed returns(bool) {
...
375:         // If a Loot Creator is set, notify it of the new Quest Period distributed
376:         if(lootCreator != address(0)) {
377:             ILootCreator(lootCreator).notifyDistributedQuestPeriod(questID, period, totalAmount);
378:         }
...
383:     }
...
269:     function _triggerCreateLoot(address user, uint256 questID, uint256 period, uint256 claimedAmount) internal {
270:         if(lootCreator != address(0)) {
271:             ILootCreator(lootCreator).notifyQuestClaim(
272:                 user,
273:                 questID,
274:                 period,
275:                 claimedAmount
276:             );
277:         }

File: LootCreator.sol
465:     function _createLoot(address user, address distributor, uint256 questId, uint256 period) internal {
...
479:         vars.userPeriodRewards = userQuestPeriodRewards[distributor][questId][period][user];
480:         if(vars.userPeriodRewards == 0) return;
481: 
482:         // Calculate ratios based on that
483:         vars.lockedRatio = (vars.userPower * UNIT) / vars.totalPower;
484: @>      vars.rewardRatio = (vars.userPeriodRewards * UNIT) / totalQuestPeriodRewards[distributor][questId][period];
485:         if(vars.rewardRatio > 0) vars.totalRatio = (vars.lockedRatio * UNIT) / vars.rewardRatio;
486: 
```

There is possible case where the Distributor changed the `lootCreator`, and user trying to `claim`, `claimQuest`, `multiClaim` which will trigger `_triggerCreateLoot` and `notifyQuestClaim` on this new `lootCreator`.

The issue here is this new `lootCreator` didn't have information of past `totalQuestPeriodRewards` which is exist on old `lootCreator`, thus when user want to `createLoot` of past period after `lootCreator` changed, it will be reverted since `totalQuestPeriodRewards` is not available in new `lootCreator`, due to division by zero on `LootCreator` in line 484.

**Attack Scenario**

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

**Recommendation**

Consider to implement a proxy for `LootCreator` to remove the feature changing lootCreator address thus keeping the past state `totalQuestPeriodRewards`
