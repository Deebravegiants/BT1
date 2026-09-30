# [M] `sharesToTokenAmount`: Division by zero

## Summary
Severity: Medium
Contest weight: 0.0802
Dataset id: 1911
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LiquidityProviders.sol#L192](https://github.com/code-423n4/2022-03-biconomy/blob/db8a1fdddd02e8cc209a4c73ffbb3de210e4a81a/contracts/hyphen/LiquidityProviders.sol#L192)  

The public `sharesToTokenAmount` function does not check if the denominator `totalSharesMinted[_tokenAddress]` is zero.  
Neither do the callers of this function. The function will revert.  
Calling functions like `getFeeAccumulatedOnNft` and `sharesToTokenAmount` from another contract should never revert.

## Recommendation
Return 0 in case `totalSharesMinted[_tokenAddress]` is zero.

A valid concern of runtime error.
