# [M] M-24 A missed requirement

## Summary
Severity: Medium
Contest weight: 0.0668
Dataset id: 8003
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Although there is a check in the takeClaimingSnapshot function (FantiumClaimingV1.sol#L686), it is more crucial to include it in the updateDistributionEventCollectionIds() function (FantiumClaimingV1.sol#L354). Implementing this check makes the previous check unnecessary, as it becomes impossible to set an empty collectionIds array for the distribution event.

## Recommendation
We recommend adding the check distributionEvents[_distributionEventId].collectionIds.length > 0 to the updateDistributionEventCollectionIds() function.
