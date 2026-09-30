# [M] Call to updatePoolRate is missing

## Summary
Severity: Medium
Contest weight: 0.0680
Dataset id: 8584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every time the totalStaked amount of a pool is updated, the updatePoolRate method is called to update the EarnRateSec. This is not true for the pauseReward method, which calls updatePool that changes the totalStaked amount. Now if a pool is paused, when it gets resumed again and updatePool is called it will calculate less rewards than it should had, because EarnRateSec was not updated.

## Recommendation
Call updatePoolRate after the updatePool call in pauseReward
Discussion
pashov: Client has fixed the issue.
