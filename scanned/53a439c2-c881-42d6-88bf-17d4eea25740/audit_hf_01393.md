# [M] M-4 AggregateStablePrice can be manipulated

## Summary
Severity: Medium
Contest weight: 0.3673
Dataset id: 7131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If there is not enough liquidity in the pools or there are no pools, then 10**18 is returned as the price in
AggregateStablePrice.
• AggregateStablePrice.vy#L151
```solidity
if D_sum == 0:
    return 10**18
```
It is supposed to be used to manipulate the price. At an early stage of the project, this can be significant.

## Recommendation
We recommend taking these conditions into account when deploying contracts.
