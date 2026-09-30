# [M] M-10 | Claiming Rewards Possible When Distributor Paused

## Summary
Severity: Medium
Contest weight: 0.0707
Dataset id: 21598
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the comments in MerkleDistributor:
Contract is pausable by owner. It allows to pause claiming rewards.
However, claimRewards doesn't have the whenNotPaused modifier. This is most likely because claimRewards calls function updateRoot which implements it. However, the call to updateRoot is conditional - it happens only if there is an upgrade possible. Otherwise, claiming is still possible - even in paused state.

## Recommendation
Add the whenNotPaused modifier to the claimRewards function.
