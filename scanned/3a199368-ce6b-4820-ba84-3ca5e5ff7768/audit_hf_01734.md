# [M] M-8 Griefing of CSModule.compensateELRewardsStealingPenalty()

## Summary
Severity: Medium
Contest weight: 0.0782
Dataset id: 9489
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CSModule.compensateELRewardsStealingPenalty() CSModule.sol#L1096-L1108. At the same time CSBondLock.sol#L126-L128 to compensate no more than what was locked. A griefer may frontrun a CSModule.compensateELRewardsStealingPenalty() call and compensate 1 locked share, causing the initial call to revert. The griefer can do this multiple times, putting the Node Operator manager at risk of having to settle their lock with a reset of the bond curve.

## Recommendation
We recommend making the CSModule.compensateELRewardsStealingPenalty() function permissioned so that only the Node Operator manager can call it.
