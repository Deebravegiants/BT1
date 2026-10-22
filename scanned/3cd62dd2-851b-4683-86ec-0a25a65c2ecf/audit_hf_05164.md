# [M] Admin can not set the pool fee

## Summary
Severity: Medium
Contest weight: 0.5410
Dataset id: 23231
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pool fee is only set in memory and not in storage so specific pool fees will not apply. The pool fee is only stored in memory.
ref: UniswapImplementation:setFee()
```solidity
PoolParams memory poolParams = _poolParams[_poolId];
poolParams.poolFee = _fee;
```
Internal pre-conditions
1. Admin calls with any fee value.
External pre-conditions
None
Attack Path
None
Specific pool fees will not apply. Only the default fee will apply to swaps.
ref: UniswapImplementation::getFee()
```solidity
uint24 poolFee = _poolParams[_poolId].poolFee;
if (poolFee != 0) {
    fee_ = poolFee;
}
```

## Recommendation
Use storage instead of memory for poolParams in .
