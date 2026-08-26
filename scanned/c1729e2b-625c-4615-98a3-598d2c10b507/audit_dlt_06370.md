# [M] Loot.sol - Updating the vestingDuration with active vests can lead to unexpected slashing

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-07
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/5
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xf605473ce1fa218c519fde45424f597361d5aef94ba601c841d5de117f2d3911
**Severity:** medium

**Description:**
**Description**\
The function ``updateVestingDuration`` is an owner controlled function.
Assuming the owner is trusted, due to the ways transactions are ordered in the blocks, there is a possible scenario for users to get slashed out of their PAL.

**Attack Scenario**\
User A (or a multiple of users) queue up a transaction for claiming loot which is past the vesting period thus full rewards are expected.
The owner queues a transaction to update the vesting duration to a larger timestamp.
User A/users whose transactions get executed after the owners transaction, due to network conditions or miners etc, will get slashed unexpectedly instead of receiving their rewards.

User funds that are left unclaimed are not lost since they are send to the creator, but they are funds that the user can never recover in full. It is a low-likelihood scenario, but due to the loss of funds I put MED.
Low could be fine IMO depending on how often the duration would be changed.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Recommendation: when creating a user loot, include the ``vestingDuration`` at the time of loot creation as part of the struct, thus the user can be sure his duration would not unexpectedly change for the worse. E.g:
```
struct LootData {
        uint256 id;
        uint256 palAmount;
        uint256 extraAmount;
        uint256 startTs;
        uint256 currentDuration; //<- add this as a fix
        bool claimed;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/5_
