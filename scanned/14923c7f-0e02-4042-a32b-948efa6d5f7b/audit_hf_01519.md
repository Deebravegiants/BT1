# [M] Some functions should be able to overflow

## Summary
Severity: Medium
Contest weight: 0.1262
Dataset id: 8034
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TickMath.sol library is missing unchecked blocks, which causes it to incorrectly revert on phantom overflow. This library was taken from https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol, but you can see solidity version is < 0.8.0, meaning that the execution didn't revert when the overflow was reached.  
This library is supposed to handle "phantom overflow" by allowing multiplication and division even when the intermediate value overflows 256 bits as documented by UniswapV3.  
In the original UniswapV3 code, unchecked is not used as solidity version is < 0.8.0, which does not revert on overflow.  
This library is used in many places in the protocol, so it is important that it is properly implemented, or it will lead to unintended results.

## Recommendation
Add the entire functions bodies of getTickAtSqrtRatio() and getTickAtSqrtRatio() to an unchecked block.  
Take a look at how Uniswap has implemented it: https://github.com/Uniswap/v3-core/blob/0.8/contracts/libraries/TickMath.sol
