# [M] ORDM-3 | Positions Can Be Liquidated On Creation

## Summary
Severity: Medium
Contest weight: 0.0939
Dataset id: 20577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While the Arbitrum sequencer is down it is possible for a users position to go from healthy to undercollateralized. During this time the average user will not be able to rescue their position as they will not be able to submit orders directly through Arbitrum. However, liquidators will be able to submit liquidation transactions through the delayed inbox on L1. When the sequencer is back online the transactions submitted through the delay box will be executed first, meaning the position will be liquidated before the users have a chance to rescue their position.

## Recommendation
Ensure that a position cannot be liquidated during its creation. Implement a validation check in the createNewPosition function.
