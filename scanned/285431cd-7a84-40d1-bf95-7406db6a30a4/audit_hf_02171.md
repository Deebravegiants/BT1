# [M] Logic Error in setPoolToRefunded()

## Summary
Severity: Medium
Contest weight: 0.3742
Dataset id: 12114
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While reviewing the State contract, we found a typo/logic error in setPoolToRefunded() when checking the pool state. Line 127 should check if the poolState is either OPEN, CLOSED, or PAID, but in the code it checked if it's not REFUNDED, twice.

```solidity
function setPoolToRefunded()
    public
    onlyPoolAdmin()
    require(poolState != PoolState.REFUNDED || poolState != PoolState.REFUNDED);
    poolState = PoolState.REFUNDED;
    emit PoolRefunded();
```

## Recommendation
No data
