# [H] Past loots can be indefinitely recreated

## Summary
Severity: High
Chain: Smart contract
Component: Paladin
Published: 2024-02-10
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/27
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xf1c478f4440222bf33173a2d0295cf02560268930a8766dbccbc8285ab906160
**Severity:** high

**Description:**
**Description**\
The ``LootCreator`` is a contract meant to manage and distribute loots, from which users can claim their accumulated rewards, based on the allocation of votes for said period and the users own reward ratios. Due to insufficient validation, valid loots can be indefinitely created.

**Attack Scenario**\
We start at the external ``createLoot``, which has no validation and simply calls the internal``_createLoot`` where:
1. The distributor is validated
2. The gauge is validated
3. The gauge, user power and rewards for the GIVEN PERIOD are taken
4. Ratios, multipliers and Pal/Extra amounts are set
5. The loot is created via a call to ``Loot(loot).createLoot``, with a start a week from the passed period.

In ``Loot(loot).createLoot``, we simply push a new loot into the loots array, where it gets a unique id, based on the array's length - there is no validation if the exact same loot has already been created for the given period.
A malicious user can recreate any past loot he wants, more favouribly his own, in order to:
1. Drain PAL and extra token from the reserve (this is possible based on the vestingDuration variable, which initially would be 28 days = 4 weeks after governance vote)
2. Greatly offset the ``pengingBudget`` variable, since no matter how old the loot we recreate is, ``pengingBudget``will always impact the newest period, tampering with future calculations

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Recommendation: when the loot for a given user, quest, gauge, disributor and most importantly - period, is created, set the ``userQuestPeriodRewards[distributor][questId][period][user]`` to 0. This way, next time we attempt to create a duplicate loot, we will face ``if(vars.userPeriodRewards == 0) return;`` and stop the attack
