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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/51_
