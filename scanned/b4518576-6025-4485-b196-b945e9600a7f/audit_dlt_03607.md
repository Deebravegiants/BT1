# [M] Missed Arbitrage Profits from Imbalanced Pools

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-06
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/101
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/d47eae920d5840afadd5fd5d1fd0d6da0107c034/src/arbitrage/ArbitrageSearch.sol#L132


# Vulnerability details

# Lines of code

https://github.com/othernet-global/salty-io/blob/d47eae920d5840afadd5fd5d1fd0d6da0107c034/src/arbitrage/ArbitrageSearch.sol#L115-L133

# C4 issue

M-16: Suboptimal arbitrage implementation


# Comments

The issue addressed the protocol's potential to overlook profitable trades due to its search range limitations. The bisection search method employed by the protocol might miss profit opportunities when the pools are balanced and a user wants to swap an amount of one token for another. This is crucial since arbitrage is a key feature that should always be available to users for capitalizing on price differences across various liquidity pools.

# Mitigation

https://github.com/othernet-global/salty-io/commit/a54656dd18135ca57eef7c4bf615b7cdff2613a7

The mitigation succesfully implemented the updated ArbitrageSearch algorithm to follow suit with the math and also the example code provided in the issue, but it additionally made sure the overflow risk is reduced since the math involves multiplications of multiple reserves(which could be substantial) primarily in the calculations of n1 and n0.

However upon further inspection, an edge case arises where if the pools were severely imbalanced, this scenario can occur:

1. One of the reserves has a MSB more than 80.
2. All reserves are shifted by "shift = maximumMSB - 80" to ensure none of them is more than 80 bits.
3. However some reserves are too low, and shifting them by this magnitude sets them to equal 0.
4. those reserves shifted to zero set n1 and n0 to 0.
5. the check that n1 <= n0 is true and function returns 0, even though n1 could have been higher than n0 before the shift.


# Impact

As with the original intention of the issue, there is potential for the algorithm to miss arbitrage profits, albeit due to a different reason and under a different circumstance, which applies here when the pools are imbalanced, and to how overflow is handled in the calculations.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/101_
