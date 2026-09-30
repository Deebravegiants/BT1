# [M] TRH-5 | Invalid Result Returned From getClaimableRewards

## Summary
Severity: Medium
Contest weight: 0.0544
Dataset id: 19568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each reward epoch restarts the accumulationIndex from 0. However in the getClaimableRewards function, the userReward.accumulationIndex is never reset when iterating through the list of epochs. Therefore the resulting claimable reward amount received from the getClaimableRewards function will be inaccurate.

## Recommendation
Reset the userReward.accumulationIndex to zero upon iterating to a new epoch.
