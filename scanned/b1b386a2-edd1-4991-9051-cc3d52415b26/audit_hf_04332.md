# [M] M-08 | Incorrect Circulating Supply Calculation

## Summary
Severity: Medium
Contest weight: 0.1196
Dataset id: 21488
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getCirculatingSupply function removes the current liquidity in bAssets from the total token supply. The goal is to determine how many bAssets can be sold into the pool. There are cases when this function returns an outdated value, due to the fact bAsset fees are not accounted for in the calculation. Consequently, the value returned might be slightly above the real value. During heavy selling of bAssets into the pool, the difference can increase as there will be more pending fees to claim. This can impact the off-chain systems for managing the operations, as the function will not return the correct state. Even if the system appears solvent using this getter function, a market making operation may revert as the real circulating supply is recalculated during the execution.

## Recommendation
Consider adding the pending fees in bAssets to the getCirculatingSupply calculation.
