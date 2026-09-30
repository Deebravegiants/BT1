# [M] Incorrect check in _calculateVirtualBalanceProd

## Summary
Severity: Medium
Contest weight: 0.3854
Dataset id: 10089
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _calculateVirtualBalanceProd function should revert if the weight is 0 or if the virtualBalance of the token is 0. However, in the implementation, it only breaks if both are 0.
```solidity
if (_weight <= 0 && _virtualBalance <= 0) {
    break;
```
This has two problems:
1. If either 1 of the values is zero, the function doesn't revert and the calculation gets processed like a normal transaction
2. The transaction isn't reverted. Instead, due to the break statement, the returned value is just equal to PRECISION. This can lead to incorrect results. The correct implementation can be found in the Yeth contract here: link

## Recommendation
Change the && to an ||, and the break to a revert.
