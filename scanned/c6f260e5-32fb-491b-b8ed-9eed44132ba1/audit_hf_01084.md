# [M] Incorrect rounding in computeSwap()

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 4148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The computeSwap function of the respective library for each LDF calculates the cumulativeAmount and swapLiquidity, which are used to obtain the amount in and amount out of a swap. The first step in the computeSwap function is to calculate roundedTick using the inverseCumulativeAmount0 or inverseCumulativeAmount1 functions. As we can see in the comments, this function will round up to the next rounded tick when the inverse tick is between two rounded ticks.
File: LibUniformDistribution.sol
```solidity
// compute roundedTick by inverting the cumulative amount
// notice that the inverse tick is between two rounded ticks,
// and we round up to the rounded tick to the right
...
(success, roundedTick) = inverseCumulativeAmount0(
    inverseCumulativeAmountInput, totalLiquidity, tickSpacing, tickLower
);
```
However, if we take a look at the implementation of these functions for the LibUniformDistribution.sol and LibGeometricDistribution.sol libraries, we can see that when the inverseCumulativeAmountInput provides a price that is very close to the rounded tick, it is not rounded up.
File: LibUniformDistribution.sol
```solidity
if (
    sqrtPrice - sqrtPriceAtTick > 1
    && (sqrtPrice - sqrtPriceAtTick).mulDiv(SQRT_PRICE_MAX_REL_ERROR, sqrtPrice) > 1
) {
    // getTickAtSqrtPrice erroneously rounded down to the
    // rounded tick boundary
    // need to round up to the next rounded tick
    tick += tickSpacing;
}
```
File: LibGeometricDistribution.sol
```solidity
// round xWad to reduce error
// limits tick precision to (ROUND_TICK_TOLERANCE / WAD) of a rounded tick
xWad = (xWad / ROUND_TICK_TOLERANCE) * ROUND_TICK_TOLERANCE; // clear small errors
...
// round xWad to reduce error
// limits tick precision to (ROUND_TICK_TOLERANCE / WAD) of a rounded tick
xWad = (xWad / ROUND_TICK_TOLERANCE) * ROUND_TICK_TOLERANCE; // clear small errors
```
The result is that the function will incorrectly return a value of swapLiquidity equal to zero, even when there is a small amount of liquidity available in the rounded tick. This will cause errors in the calculation of the amount in and amount out of a swap. Given that the rest of LDFs are built on top of the UniformDistribution and GeometricDistribution LDFs, this will affect all of them.

## Recommendation
Consider rounding up to the next rounded tick any time the sqrtPrice is equal to sqrtPriceAtTick.
