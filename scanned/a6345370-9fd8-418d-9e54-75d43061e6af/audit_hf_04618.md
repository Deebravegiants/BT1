# [M] M-45 | DOS Of depositFromPairedLpToken

## Summary
Severity: Medium
Contest weight: 0.1025
Dataset id: 22223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In depositFromPairedLpToken, if a swap of a reward token fails, an override feature kicks in to halve and store the next _amountIn to swap in _rewardsSwapAmountInOverride. A temporary DOS attack is possible by making use of this feature: 1. Deposit 50 wei of the reward token. The small swap to Uniswap V3 would fail due to insuﬃcient amountOut. 2. Half of 50 wei (i.e. 25 wei) will then be stored in _rewardsSwapAmountInOverride. 3. Contract will attempt to swap for another 6 times before the override amount is set to zero — preventing actual rewards from being processed.

## Recommendation
Consider redesigning the override design for swap failures.
