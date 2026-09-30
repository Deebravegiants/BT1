# [H] H-02 | Oracle Price DoS

## Summary
Severity: High
Contest weight: 0.2121
Dataset id: 2154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function oraclePriceSqrtX96 aims to calculate the oracle price by gathering the TWAP across all Uniswap pools with a specific (token0, token1) pair and calculating the mean. The pre-condition for a successful call to oraclePriceSqrtX96 is that for each Uniswap pool in the poolsList, the consult function does not revert. However, if a pool was just created, there would not be an observation that was ORACLE_T seconds ago and Uniswap's observeSingle would revert: "dev Reverts if an observation at or before the desired observation timestamp does not exist" Ultimately, a user can DoS the calculation of oracle pricing for an entire period just by deploying a different fee tier, which would prevent positionData retrieval and DoS other areas of the codebase such as function isUnderwater and consequently restructureBadDebt.

## Recommendation
Consider wrapping the call to Uniswap's observe in a try-catch and then adjusting the number of observations by how many calls were successful.
