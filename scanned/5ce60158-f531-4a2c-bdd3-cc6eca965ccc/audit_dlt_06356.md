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
function notifyDistributedQuestPeriod(uint256 questId, uint256 period, uint256 totalRewards) external onlyAllowedDistributor nonReentrant {
    uint256 gaugeWeight = ILootVoteController(lootVoteController).getGaugeRelativeWeightWrite(gauge, period);
    uint256 gaugeCap = ILootVoteController(lootVoteController).getGaugeCap(gauge);
    Budget memory budget = periodBudget[period];

    // If the gauge weight is higher than the cap, we need to handle the un-allocated rewards
    if(gaugeWeight > gaugeCap) {
        uint256 unsunedWeight = gaugeWeight - gaugeCap;

        gaugeWeight = gaugeCap; // ==> @audit, change gauge weight

        // Handle un-allocated budget => set it as pending for next periods
        pengingBudget.palAmount += uint128(uint256(budget.palAmount) * unsunedWeight / UNIT);  
        pengingBudget.extraAmount += uint128(uint256(budget.extraAmount) * unsunedWeight / UNIT);
    }
    // Calculate the allocated budget for the gauge
    uint256 palAmount = uint256(budget.palAmount) * gaugeWeight / UNIT;
    uint256 extraAmount = uint256(budget.extraAmount) * gaugeWeight / UNIT;

    // Update the allocated budget history
    allocatedBudgetHistory[period].palAmount += uint128(palAmount);  // @audit, no consideration for the amounts added to pendingBudget
    allocatedBudgetHistory[period].extraAmount += uint128(extraAmount);

    gaugeBudgetPerPeriod[gauge][period] = Budget(
        uint128(palAmount),
        uint128(extraAmount)
    );
}
```
- Then, in the upcoming `_updatePeriod` function, the `20%` amounts will be duplicated.
```
function _updatePeriod() internal {
    Budget memory pending = pengingBudget; // ==> @audit, includes 20% 

    Budget memory previousBudget = periodBudget[lastFinishedPeriod];
    Budget memory previousSpent = allocatedBudgetHistory[lastFinishedPeriod];  // ==> @audit, the 20% was not considered here
    pending.palAmount += previousBudget.palAmount - previousSpent.palAmount;
    pending.extraAmount += previousBudget.extraAmount - previousSpent.extraAmount;

    periodBudget[nextBudgetUpdatePeriod] = pending;
}
```
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Mark the exceeding amounts as allocated as well
```
function notifyDistributedQuestPeriod(uint256 questId, uint256 period, uint256 totalRewards) external onlyAllowedDistributor nonReentrant {
    if(gaugeWeight > gaugeCap) {
        uint256 unsunedWeight = gaugeWeight - gaugeCap;

        gaugeWeight = gaugeCap;

        // Handle un-allocated budget => set it as pending for next periods
+        uint128 unsunedPal = uint128(uint256(budget.palAmount) * unsunedWeight / UNIT);
+        uint128 unsunedExtra = uint128(uint256(budget.extraAmount) * unsunedWeight / UNIT);

-         pengingBudget.palAmount += uint128(uint256(budget.palAmount) * unsunedWeight / UNIT);
-         pengingBudget.extraAmount += uint128(uint256(budget.extraAmount) * unsunedWeight / UNIT);

+        pengingBudget.palAmount += unsunedPal ;
+        pengingBudget.extraAmount += unsunedExtra;

+         allocatedBudgetHistory[period].palAmount += unsunedPal ;
+         allocatedBudgetHistory[period].extraAmount += unsunedExtra ;
    }
}
```
