# [M] `_createLoot` should allow user to create their past loot even though recently the distributor is removed

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-15
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/59
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0x253b61a5ec1b171eb1bfd199fbdf4942aec3b7ab5f9158213f2bc58f20fd056e
**Severity:** medium

**Description:**
**Description**

In `_createLoot` there is a condition check to verify if `distributor` is allowed or not. Distributor is not allowed if it's never been added (via `addDistributor`), or distributor already removed (via `removeDistributor`).

```js
File: LootCreator.sol
465:     function _createLoot(address user, address distributor, uint256 questId, uint256 period) internal {
466:         CreateVars memory vars;
467: @>      if(!allowedDistributors[distributor]) return;
468:         
```

The `_createLoot` itself can be called any time user want, user can create past loot period. Knowing this condition, there is concern if user is not creating loot, waiting for a batch creation using `createMultipleLoot`, meanwhile distributor at some period is removed.

If distributor is removed, and if user want to `createLoot` of past period from that removed distributor, because of the `allowedDistributor` condition check, user will failed to create loot.

We can't just prevent this distributor removal on `removeDistributor` if the distributor already notify distribution. We just need to make sure if distributor removed, user can still create loot of the past period. One way to do this, is to check if `totalQuestPeriodRewards` is not 0, then the user can stil create loot. For example, please take a look at diff snippet below.

**Attack Scenario**

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

```diff
File: LootCreator.sol
465:     function _createLoot(address user, address distributor, uint256 questId, uint256 period) internal {
466:         CreateVars memory vars;
--           if(!allowedDistributors[distributor]) return;
++           if(!allowedDistributors[distributor] && totalQuestPeriodRewards[distributor][questId][period] == 0) return;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/59_
