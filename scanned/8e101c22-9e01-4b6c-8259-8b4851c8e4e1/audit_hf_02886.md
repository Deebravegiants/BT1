# [M] TWAP can be manipulated

## Summary
Severity: Medium
Contest weight: 0.1295
Dataset id: 16186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract uses the TWAP oracle to calculate the price for deposits and
swaps performed through the pump mechanism. The observation window is set
to 18.15 minutes.
However, two issues cause the TWAP to be easily manipulated:
1. Uniswap V3 pools are initialized with an observation cardinality of 1, which
means that the TWAP oracle will only consider the last price update.
2. Even if the observation cardinality is high enough for the observation
window, the number of observations recorded might not be enough.
This means that an attacker could manipulate the price of the ULTI token.
Given that both the deposit and the pump functions have slippage protection
mechanisms, the outcome of the attack would be the DoS for these functions.

## Recommendation
1. Call the IUniswapV3Pool.increaseObservationCardinalityNext(uint16
observationCardinalityNext) function after the initialization of the pool
with a value high enough to cover the observation window. This value
should be at least observationWindow /
averageBlockProductionRageOfTheNetwork.
2. Ensure the number of observations recorded is high enough to cover the
observation window.
