# [M] 6.32 Possible Underflow in UniV3Oracle.price

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The UniV3Oracle computes the price of two tokens based on two observations obs1 and obs0 from
the Uniswap. The respective code is:

```
uint256 obs1 = (uint256(observationIndex) + uint256(observationCardinality) - 1) %
uint256(observationCardinality);
uint256 obs0 = (uint256(observationIndex) + uint256(observationCardinality) - bfAvg) %
uint256(observationCardinality);
int256 tickAverage;
{
(uint32 timestamp0, int56 tick0, , ) = IUniswapV3Pool(pool).observations(obs0);
(uint32 timestamp1, int56 tick1, , ) = IUniswapV3Pool(pool).observations(obs1);
uint256 timespan = timestamp1 - timestamp0; // reverts
...
}
```
The obj1 points to the previous observation (the one before the most recent observation), while the
obj0 should point to bfAvg observations before obj1. However, in case:

```
bfAvg == observationCardinality
```
obj0 would point to the most recent observation, which would have a more recent timestamp than obj1,
hence the statement to compute timespan would cause an underflow which reverts.

Code corrected:


The possibility of the underflow as described above has been mitigated in the updated code as the
bfAvg cannot be equal to obersvationCardinality:

```
if (observationCardinality <= bfAvg) {
continue;
}
```
Note that, the oracle does not return a price if for some pool bfAvg is equal to the observations
cardinality.
