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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/56_
