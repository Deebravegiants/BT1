# [H] Usage of slot0 is extremely easy to manipu-

## Summary
Severity: High
Contest weight: 0.1652
Dataset id: 20486
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Usage of slot0 is extremely easy to manipulate Real Wagmi is using slot0 to calculate several variables in their codebase: ntracts/Multipool.sol#L589-L596 slot0 is the most recent data point and is therefore extremely easy to manipulate. Multipool directly uses the token values returned by getAmountsForLiquidity to calculate the reserves. Which they are used to calculate the lpAmount to mint from the pool. This allows a malicious user to manipulate the amount of the minted by a user. ntracts/Multipool.sol#L483 ntracts/Multipool.sol#L458 Pool lp value can be manipulated and cause other users to receive less lp tokens.

## Recommendation
To make any calculation use a TWAP instead of slot0.
