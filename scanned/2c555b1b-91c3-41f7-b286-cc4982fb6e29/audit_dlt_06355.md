# [M] There's no guarantee that the period updates continuously in LootCreator

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-13
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/51
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xd60b2a57fbcee8f5b277914c96b660c20fe206b1650244efb1a31badd49c38cd
**Severity:** medium

**Description:**
**Description**\
We have an important function called `_updatePeriod` in `LootCreator`.
Within this function, we update the current period budget, handle pending budgets, and update some critical `variables`. 
It's essential to execute these updates correctly to ensure receiving PAL and extra token rewards.

**Attack Scenario**\
- We have a variable called `nextBudgetUpdatePeriod`, and we initialize its initial value in the `constructor`.
```
constructor(address _loot, address _lootVoteController, address _holyPower) {
    nextBudgetUpdatePeriod = (block.timestamp + WEEK) / WEEK * WEEK;   // ===> @audit
}
```
- There's no guarantee that this value is always up to date. For instance, it might not be updated after deployment until the first reward claiming occurs, or there could be a gap of several weeks between rewards claiming, and so on.
- When the `distributor` notifies the `LootCreator`, it invokes the `_updatePeriod` function.
```
function notifyDistributedQuestPeriod(uint256 questId, uint256 period, uint256 totalRewards) external onlyAllowedDistributor nonReentrant {
    _pullBudget();
    _updatePeriod();  // ==> @audit, here
}
```
- In the `_updatePeriod` function, we cannot be sure that `nextBudgetUpdatePeriod` is larger than the `period`.
```
function _updatePeriod() internal {
    if(block.timestamp < nextBudgetUpdatePeriod) return;
    periodBlockCheckpoint[nextBudgetUpdatePeriod] = block.number;
    
    periodBudget[nextBudgetUpdatePeriod] = pending;
    nextBudgetUpdatePeriod += WEEK;
}
```

This can lead to several vulnerabilities.

- Because the `period` is larger than `nextBudgetUpdatePeriod`, the `periodBudget[period]` is `0`, so `gaugeBudgetPerPeriod` is also `0`. And we only allocate the `gauge` for the `period` once.
  This means that users cannot claim rewards for this `gauge` and `period`.
```
function notifyDistributedQuestPeriod(uint256 questId, uint256 period, uint256 totalRewards) external onlyAllowedDistributor nonReentrant {
    if(isGaugeAllocatedForPeriod[gauge][period]) return;   // ==> @audit, only once
    isGaugeAllocatedForPeriod[gauge][period] = true;
    
    Budget memory budget = periodBudget[period];  // ==> @audit, 0
    
    uint256 palAmount = uint256(budget.palAmount) * gaugeWeight / UNIT;
    uint256 extraAmount = uint256(budget.extraAmount) * gaugeWeight / UNIT;

    gaugeBudgetPerPeriod[gauge][period] = Budget(
        uint128(palAmount),
        uint128(extraAmount)
    );  // ==> @audit, also 0
}
```
- And also, the `_createLoot` function may not work correctly because `periodBlockCheckpoint[period]` is not updated yet.
```
function _createLoot(address user, address distributor, uint256 questId, uint256 period) internal {
    vars.totalPower = IHolyPowerDelegation(holyPower).total_locked_at(periodBlockCheckpoint[period]);
    vars.lockedRatio = (vars.userPower * UNIT) / vars.totalPower;
}
```

Of course, there is an external function called `updatePeriod`, and if we trust that a trusted entity always ensures the proper update, there is no need to call this function when the distributor notifies the `LootCreator`.
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Modify `_updatePeriod` function.
```
function _updatePeriod() internal {
-     if(block.timestamp < nextBudgetUpdatePeriod) return;

+    while (nextBudgetUpdatePeriod <= block.timestamp) {
            // Save the current block number for checkpointing
            periodBlockCheckpoint[nextBudgetUpdatePeriod] = block.number;
    
            // Update the current period budget
            Budget memory pending = pengingBudget;
            pengingBudget = Budget(0, 0);
    
            // 2 weeks difference to not impact the current distribution and allocations
            uint256 lastFinishedPeriod = nextBudgetUpdatePeriod - (WEEK * 2);
            Budget memory previousBudget = periodBudget[lastFinishedPeriod];
            Budget memory previousSpent = allocatedBudgetHistory[lastFinishedPeriod];
            pending.palAmount += previousBudget.palAmount - previousSpent.palAmount;
            pending.extraAmount += previousBudget.extraAmount - previousSpent.extraAmount;
    
            // Save the new set budget
            periodBudget[nextBudgetUpdatePeriod] = pending;
    
            nextBudgetUpdatePeriod += WEEK;
+     }
}
```
