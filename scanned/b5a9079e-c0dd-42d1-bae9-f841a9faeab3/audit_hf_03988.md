# [H] Oracle.sol: manipulation via increasing Uniswap

## Summary
Severity: High
Contest weight: 0.6384
Dataset id: 20362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The attack path is quite involved. However by exploiting this issue, the TWAP price can be manipulated as well as implied volatility (IV) and the probe prices. The Oracle.consult function takes a uint40 seed parameter and can be used in either of two ways: 1. Set the highest 8 bit to a non-zero value to use Uniswap V3’s binary search to get observations 2. Set the highest 8 bit to zero and use the lower 32 bits to provide hints and use the more efficient internal Oracle.observe function to get the observations. The code for Aloe's Oracle.observe function is adapted from Uniswap V3's Oracle library. To understand this issue it is necessary to understand Uniswap V3's observationCardinality concept. A deep dive can be found here. In short, it is a circular array of variable size. The size of the array can be increased by ANYONE via calling Pool.increaseObservationCardinalityNext. The Uniswap V3 Oracle.write function will then take care of actually expanding the array once the current index has reached the end of the array. As can be seen in this function, uninitialized entries in the array have their timestamp set to 1. And all other values in the observation struct (array element) are set to zero:
```solidity
struct Observation {
    // the block timestamp of the observation
    uint32 blockTimestamp;
    // the tick accumulator, i.e. tick * time elapsed since the pool was first initialized
    int56 tickCumulative;
    // the seconds per liquidity, i.e. seconds elapsed / max(1, liquidity) since the pool was first initialized
    uint160 secondsPerLiquidityCumulativeX128;
    // whether or not the observation is initialized
    bool initialized;
}
```
Here's an example for a simplified array to illustrate how the Aloe Oracle.observe function might read an invalid value: Assume we are looking for the target=10 timestamp. And the observations array looks like this (element values are timestamps): | 12 | 20 | 25 | 30 | 1 | 1 | 1 | The length of the array is 7. Let's say we provide the index 6 as the seed and the current observationIndex is 3 (i.e. pointing to timestamp 30). The Oracle.observe function then chooses 1 as the left timestamp and 12 as the right timestamp. This means the invalid and uninitialized element at index 6 with timestamp 1 will be used to calculate the Oracle values. Here is the section of the Oracle.observe function where the invalid element is used to calculate the result. By updating the observations (e.g. swaps in the Uniswap pool), an attacker can influence the value that is written on the left of the array, i.e. he can arrange for a scenario such that he can make the Aloe Oracle read a wrong value. Upstream this causes the Aloe Oracle to continue calculation with tickCumulatives and secondsPerLiquidityCumulativeX128s having a corrupted value. Either secondsPerLiquidityCumulativeX128s[0], tickCumulatives[0] AND secondsPerLiquidityCumulativeX128s[1], tickCumulatives[1] or only secondsPerLiquidityCumulativeX128s[0], tickCumulatives[0] are assigned invalid values (depending on what the timestamp on the left of the array is). The corrupted values are then used in the further calculations in Oracle.consult which reports its results upstream to VolatilityOracle.update and VolatilityOracle.consult, making their way into the core application. The TWAP price can be inflated such that bad debt can be taken on due to inflated valuation of Uniswap V3 liquidity. Besides that there are virtually endless possibilities for an attacker to exploit this scenario since the Oracle is at the very heart of the Aloe application and it's impossible to foresee all the permutations of values that a determined attacker may use. E.g. the TWAP price is used for liquidations where an incorrect TWAP price can lead to profit. If the protocol expects you to exchange 1 BTC for 10k USDC, then you end up with ~20k profit. Since an attacker can make this scenario occur on purpose by updating the Uniswap observations (e.g. by executing swaps) and increasing observation cardinality, the severity of this finding is "High".

## Recommendation
The Oracle.observe function must not consider observations as valid that have not been initialized. This means the initialized field must be queried here and here and must be skipped over.
