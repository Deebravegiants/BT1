# [M] Cannot use CurveSwapper when calling compound due to mismatched data parameter

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1280
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/master/contracts/aave/AaveStrategy.sol#L192
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/master/contracts/curve/TricryptoNativeStrategy.sol#L169
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/master/contracts/convex/ConvexTricryptoStrategy.sol#L206
https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/master/contracts/curve/TricryptoLPStrategy.sol#L178


# Vulnerability details

## Impact
When `swapper.getOutputAmount` is reached `swapData` and a blank string, `""`, are passed. CurveSwappers’ `getOutputAmount` expects `dexOption`s to be an array of `uint256`, not a blank string, `“”`. As a result, the transaction will revert which will prevent these strategies from compounding. 

## Proof of Concept
1. Aave strategy is deployed with CurveSwapper as its swapper
2. A caller calls compound but the transaction reverts 

## Tools Used
manual

## Recommended Mitigation Steps
If CurveSwapper ensure that the correct parameters are passed


## Assessed type

DoS
