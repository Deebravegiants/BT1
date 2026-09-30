# [M] M-03 | Exit Loop Before Borrow Operation

## Summary
Severity: Medium
Contest weight: 0.0514
Dataset id: 22057
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the function _loop, an early exit occurs if minimumCollateral is hit. This is called after the borrow operation. However, if _bAssetsIn is too small, the borrow operation could revert as no new principal is transferred out. This would result in the entire reheat operation reverting.

## Recommendation
The early exit for minimumCollateral should be done before the borrow operation.
