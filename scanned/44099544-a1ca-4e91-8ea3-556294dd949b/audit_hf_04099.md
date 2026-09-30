# [M] DATA-2 | Updating A Market After Pause Incurs Fees

## Summary
Severity: Medium
Contest weight: 0.0984
Dataset id: 20555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Updating an existing market, by calling the updateExistingMarket function from the DataFabric contract, incorrectly also calculates market fees up to that point. This is because it also includes a call to the _updateCumulativeFees function, which is responsible for updating fees up to that point. The updateExistingMarket function cannot be called if the market is not paused, but pausing the market does not fast forward feeLastUpdatedTimestamp, only unpausing does. For the time since the market was paused and until it was updated by the admin, the market will incorrectly deduct fees from participants.

## Recommendation
Delete the call to the _updateCumulativeFees function since a call to it is already done in the pause function.
