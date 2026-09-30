# [M] Withdrawals will stuck

## Summary
Severity: Medium
Contest weight: 0.6489
Dataset id: 18086
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract separates the accounting of staked RSR (stakeRSR) from the accounting of withdrawal drafts (draftRSR) by using two independent era counters: a staking era and a draft era. When a seizure operation reduces stakeRSR to zero or pushes the stake rate above a configured maximum, the contract calls beginEra, which resets the staking state and increments the staking era. At that moment the draft era is left unchanged if draftRSR is still positive, so pending withdrawal drafts remain attached to the previous draft era. Later, if a subsequent seizure causes the draft rate to exceed its maximum, beginDraftEra is invoked, advancing the draft era while the previously created drafts still reference the older draft era. Because the pushDraft function stores drafts in a mapping keyed by the current draftEra, any drafts that were created while the draftEra lagged behind the staking era become unreachable once the draftEra is incremented. From a user’s perspective the balance shown in the UI may still indicate an amount ready for withdrawal, but the withdrawal call returns zero or reverts because the contract looks for drafts in the new era where none exist. This mismatch can happen whenever stakeRSR is exhausted before draftRSR, which is a realistic scenario during large seizure events or rounding edge‑cases. The impact is that users who have unstaked RSR and are waiting for their draft to become claimable may lose the ability to withdraw those funds, effectively locking or wiping their holdings. The issue was identified during a manual audit by constructing a proof‑of‑concept that forces the two era counters out of sync and then demonstrates that a user’s draft entry is orphaned after the draft era advances. The bug is subtle because the contract emits no explicit error and the internal counters are not exposed directly, making it easy to miss in functional testing. The appropriate remediation is to enforce that the draft era is updated together with the staking era whenever either counter is advanced, or to prevent the draft era from advancing while there exist pending drafts, or to store drafts in a way that is independent of the era index (for example by using a per‑user list that does not rely on a global era key). Aligning the two eras restores the invariant that every unstaked amount has a corresponding, claimable draft, thereby preventing funds from becoming permanently inaccessible.

## Proof of Concept
1. seizeRSR is called with amount 150 where stakeRSR was 50 and draftRSR was 80. The era was 1 currently for both stake and draft

```solidity
function seizeRSR(uint256 rsrAmount) external notPausedOrFrozen {
...
stakeRSR -= stakeRSRToTake;
..
if (stakeRSR == 0 || stakeRate > MAX_STAKE_RATE) {
            seizedRSR += stakeRSR;
            beginEra();
        }
...
draftRSR -= draftRSRToTake;
if (draftRSR > 0) {
            // Downcast is safe: totalDrafts is 1e38 at most so expression maximum value is 1e56
            draftRate = uint192((FIX_ONE_256 * totalDrafts + (draftRSR - 1)) / draftRSR);
        }

...
```

2. stakeRSR portion comes to be 50 which means remaining stakeRSR will be 0 (50-50). This means a new staking era will get started

```solidity
if (stakeRSR == 0 || stakeRate > MAX_STAKE_RATE) {
            seizedRSR += stakeRSR;
            beginEra();
        }
```

3. This causes staking era to become 2

```solidity
function beginEra() internal virtual {
        stakeRSR = 0;
        totalStakes = 0;
        stakeRate = FIX_ONE;
        era++;

        emit AllBalancesReset(era);
    }
```

4. Now draftRSR is still > 0 so only draftRate gets updated. The draft Era still remains 1
5. User stakes and unstakes in this new era. Staking is done in era 2
6. Unstaking calls the pushDraft which creates User draft on draftEra which is still 1

```solidity
function pushDraft(address account, uint256 rsrAmount)
        internal
        returns (uint256 index, uint64 availableAt)
    {
...
CumulativeDraft[] storage queue = draftQueues[draftEra][account];
       ...

        queue.push(CumulativeDraft(uint176(oldDrafts + draftAmount), availableAt));
...
}
```

7. Lets say due to unfortunate condition again seizeRSR need to be called. This time `draftRate > MAX_DRAFT_RATE` which means draft era increases and becomes 2

```solidity
if (draftRSR == 0 || draftRate > MAX_DRAFT_RATE) {
            seizedRSR += draftRSR;
            beginDraftEra();
        }
```

8. This becomes a problem since all unstaking done till now in era 2 were pointing in draft era 1. Once draft era gets updated to 2, all those unstaking are lost.

## Recommendation
Era should be same for staking and draft. So if User is unstaking at era 1 then withdrawal draft should always be era 1 and not some previous era.

I believe the sequence of events here to be off with when beginDraftEra would be called.

Will leave open for sponsor confirmation on the beginDraftEra call being triggered earlier in the process due to the value of `draftRSR == 0`. 

In the example described, I’m pretty sure point 4 is wrong: draftRSR would be 0 and both the eras would be changed at the same time.

That said, I don’t think it’s a problem to have different eras for stakeRSR and draftRSR. It’s subtle, but it could be that due to rounding one of these overflows `MAX_STAKE_RATE`/`MAX_DRAFT_RATE`, but not the other. This is fine. This means enough devaluation has happened to one of the polities (current stakers; current withdrawers) that they have been wiped out. It’s not a contradiction for the other polity to still be entitled to a small amount of RSR.

It also might be the warden is misunderstanding the intended design here: if you initiate StRSR unstaking, then a sufficient RSR seizure event _should_ result in the inability to withdraw anything after. 

Please note: the following comment and re-assessment took place after judging and awarding were finalized. As such, this report will leave this finding in its originally assessed risk category as it simply reflects a snapshot in time.

I wanted to comment and apologize that this issue slipped through the QA process and I didn’t give it a second pass to close it out as invalid. While C4 will not change grades or awards retroactively, it is worth noting for the final report that I do not believe this issue to be valid.
