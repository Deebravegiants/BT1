# [M] getPendingCommits() underreports commits

## Summary
Severity: Medium
Contest weight: 0.5467
Dataset id: 16063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
When frontRunningInterval > updateInterval, the PoolCommitter.getAppropriateUpdateIntervalId() function can return updateInterval IDs that are arbitrarily far into the future, especially if appropriateIntervalId > updateIntervalId + 1.
Therefore, commits can also be made to these appropriate interval IDs far in the future by calling commit(). The PoolCommitter.getPendingCommits() function only checks the commits for updateIntervalId and updateIntervalId + 1, but needs to check up to updateIntervalId + factorDifference + 1.
Currently, it is underreporting the pending commits which leads to the checkInvariants function not checking the correct values.
```

## Recommendation
```solidity
The getPendingCommits function should return all possible pending commits even in the case where frontRunningInterval > updateInterval.
```
