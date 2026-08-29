# [M] Risk of overflow

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/29
Type: sherlock-finding

## Details
8olidity

medium

# Risk of overflow

## Summary
Risk of overflow
## Vulnerability Detail
There are two risks of spillover
1. It uint256 type to int56 directly

`batch.poolToken_redeem` and `pric`e are doing multiplication operations that will most likely exceed the size of int256

2. Match the int128 to the int256

The small precision value decreases the large type of data, it is very likely to overflow



## Impact
Risk of overflow
## Code Snippet
https://github.com/sherlock-audit/2022-11-float-capital/blob/main/contracts/market/template/MarketCore.sol#L577
```solidity
  function _processAllBatchedEpochActions(
    uint256 associatedEpochIndex,
    PoolType poolType,
    uint256 poolTier,
    uint256 price,
    address poolToken
  ) internal returns (int256 changeInMarketValue_inPaymentToken) {
    // QUESTION: is it worth the gas saving this storage pointer - we only use 'pool' twice in this function.
    Pool storage pool = pools[poolType][poolTier];

    BatchedActions memory batch = pool.batchedAmount[associatedEpochIndex & 1];

    // Only if mints or redeems exist is it necessary to adjust supply and collateral.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/29_
