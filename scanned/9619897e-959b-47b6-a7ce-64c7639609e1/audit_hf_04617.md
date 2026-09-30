# [M] M-44 | Swap Error Handling Causes DOS Of AutoCompounder

## Summary
Severity: Medium
Contest weight: 0.1158
Dataset id: 22222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _processRewardsToPodLp, if a swap of the main reward token fails, an override feature kicks in to halve and store the next _amountIn to swap in _tokenToPairedSwapAmountInOverride. A temporary DOS attack can be carried out as such: 1. Donate 50 wei of the main reward token (PEAS), assuming contract has no previous balance of PEAS. 2. Call deposit to trigger _processRewardsToPodLp where the small swap to Uniswap V3 would fail due to insuﬃcient amountOut. 3. Half of 50 wei (i.e. 25 wei) will then be stored in the override mapping. 4. Contract will attempt to swap for another 6 times before the override amount is set to zero — preventing actual rewards from being processed.

## Recommendation
Consider re-designing the error handling for the swap.
