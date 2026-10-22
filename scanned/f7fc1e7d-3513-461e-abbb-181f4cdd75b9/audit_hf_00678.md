# [H] H-03 | Newly Added Strategy Provider Will Not Receive LP Deposits

## Summary
Severity: High
Contest weight: 0.2319
Dataset id: 2214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Under the current proportional deposit logic in allocatToFunds, the contract allocates newly deposited LP assets among strategies based solely on the main vault’s existing shares (i.e., mainShares). When a new strategy provider is introduced at a later period (for example, in the period 5), it starts with zero main shares. Consequently, the formula: portionForThisStrategy = pendingLpDepositAssets * (mainAssetsInFund / totalMainAssetsInFund) will yield zero for that strategy. The new strategy never accumulates any main vault capital automatically, as it isn’t part of the existing distribution ratio (which depends on mainShares). Even if the new strategy invests its own capital (SP deposit), that action mints strategy provider shares, not main shares, thus it does not affect the main vault ratio or future LP deposit splits. As a result, this new strategy remains perpetually excluded from LP inflows.

## Recommendation
Incorporate a method for the operator to allocate a desired seed amount of main vault capital to a newly added strategy (e.g., “rebalance from existing strategies” to ensure the newcomer starts with a non-zero main share).
