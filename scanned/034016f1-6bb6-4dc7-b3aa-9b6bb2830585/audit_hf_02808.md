# [M] Code doesn't work with fee on transfer tokens

## Summary
Severity: Medium
Contest weight: 0.0839
Dataset id: 15383
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are some places in the code that assume the ERC20 transfer function will transfer a specified amount and this is not true for tokens with fee. This will cause wrong calculation results in those cases. Some of the places where this issue happens:
1. In _addInitialLiquidity() code assumes it transfers _initialLiquidityInIBT tokens and tries to transfer them to the Curve pool.
2. In _dispatchPreviewRate() code assumes it would transfer value from the user.

## Recommendation
Consider significant code modifications (managing actual balances) or prevent fee-on-transfer from appearing during code execution or acknowledge that these tokens will always have wrong calculation
