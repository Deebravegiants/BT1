# [M] Some rewards are being duplicated

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-12
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/47
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xf590d3d3414c464cb66ef2d1f3c53cccc7444e36fde07e15c35c26946d9e3af7
**Severity:** medium

**Description:**
**Description**\
There can be `reward` duplication  when the `gauge` weight exceeds the `cap`.

**Attack Scenario**\
- When we call the `updateQuestPeriod` function in `MultiMerkleDistributorV2`, it invokes the `notifyDistributedQuestPeriod` function of the `LootCreator`.
```
function updateQuestPeriod(uint256 questID, uint256 period, uint256 totalAmount, bytes32 merkleRoot) external onlyAllowed returns(bool) {
    if(lootCreator != address(0)) {
        ILootCreator(lootCreator).notifyDistributedQuestPeriod(questID, period, totalAmount);
    }
}
```
- The `notifyDistributedQuestPeriod` function invokes the `_updatePeriod` function, where we utilize the sum of `pending budget` and the not-allocated budget from `2` weeks ago as the current period's budget.
```
function _updatePeriod() internal {
     Budget memory pending = pengingBudget;  // ==> pending budget
     pengingBudget = Budget(0, 0);

     uint256 lastFinishedPeriod = nextBudgetUpdatePeriod - (WEEK * 2);
     Budget memory previousBudget = periodBudget[lastFinishedPeriod];
     Budget memory previousSpent = allocatedBudgetHistory[lastFinishedPeriod];
     pending.palAmount += previousBudget.palAmount - previousSpent.palAmount;   // ==> non-allocated portion
     pending.extraAmount += previousBudget.extraAmount - previousSpent.extraAmount;

     // Save the new set budget
     periodBudget[nextBudgetUpdatePeriod] = pending;
}
```
- In the `notifyDistributedQuestPeriod` function, if the weight of that `gauge` exceeds the `cap`, we add these exceeding amounts to the pending budget to use in the next periods.
  The problem is that we don't consider these exceeding amounts as part of the allocated budget.
  For example, if the `gauge` weight is `30%` and the `cap` is `10%`, then `20%` is added to the `pending budget` and `10%` to the `gaugeBudgetPerPeriod`, but only `10%` is marked as allocated.
```
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/47_
