# [M] Uniswap V3 pool cardinality should not be hardcoded to 60 in MemeFactory._createUniswapPair()

## Summary
Severity: Medium
Contest weight: 0.4320
Dataset id: 5723
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In MemeFactory._createUniswapPair(), whenever a new Uniswap V3 pool is created, increaseObservationCardinalityNext() is called with a hardcoded value of 60:
```solidity
// Increase observation cardinality
IUniswapV3(pool).increaseObservationCardinalityNext(60);
```
However, this leads to two issues:
1. A cardinality of 60 is too small.
2. Cardinality should not be hardcoded to the same value across different chains.
Calling increaseObservationCardinalityNext() increases the cardinality of the pool, which is the maximum number of observations that can be stored. Considering that an observation is stored at most once per block, the cardinality of the pool must be large enough to cover the desired TWAP window when observe() is called (ie. should be at least twapWindowSeconds / secondsPerBlock).
Regarding (1), Base produces a block every 2 seconds. Assuming an observation is stored every block, setting cardinality = 60 limits the oldest observation to 2 * 60 = 120 seconds ago, which is extremely short and susceptible to manipulation.
Regarding (2), the cardinality should be set depending on the block time of each chain. Since BuyBackBurner uses an observation window of 1800 seconds (BuyBackBurner.sol#L57-L58), the minimum cardinality for Base and Celo should be:
• Base - 1800 / 2 = 900.
• Celo - 1800 / 5 = 360.

## Recommendation
Consider calling increaseObservationCardinalityNext() with a virtual _observationCardinalityNext() function that is overridden in MemeBase and MemeCelo to return the appropriate values:
```diff
// Increase observation cardinality
- IUniswapV3(pool).increaseObservationCardinalityNext(60);
+ IUniswapV3(pool).increaseObservationCardinalityNext(_observationCardinalityNext());
```
