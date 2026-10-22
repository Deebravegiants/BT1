# [M] No clear threshold on when the oracle is up-

## Summary
Severity: Medium
Contest weight: 0.1252
Dataset id: 20044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
No clear threshold on when the oracle is updated will cause stale prices to be accepted. "The oracle price update is limited by cost of gas fee during updating. We want to have a balance between reaching the true price vs saving the cost. Once we move to cheaper chains like arbitrum or matic, we will update the oracle a lot more frequently just fyi." Not having a clear point in time when the oracle will be updated, will cause that in times when the network is very expensive to include transactions, stale prices of assets/stables will be accepted as the current price, causing wrong/stale prices to be fetched as if they were the latest. Wrong/stale prices will be used in times when gas fees are very expensive. Code Snippet8 3b0fd4595e4eb6b732a40e421e/Unitas-Protocol/src/XOracle.sol#L34-L46.

## Recommendation
Add a clear threshold when the prices should be updated (ex. each 2 minutes), potentially not using the gas fees as an indicator to when updating the oracle.
