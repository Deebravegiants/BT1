# [M] Curve values are not checked to be in increasing order. Leading to revert of several core functions.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/92
Type: sherlock-finding

## Details
ElKu

medium

# Curve values are not checked to be in increasing order. Leading to revert of several core functions.

## Summary

The curve values in `TimeLockPool.sol` are not checked to be in increasing order, which might result in all functions which uses the `getMultiplier` function to revert. 

## Vulnerability Detail

Looking at the `getMultiplier` code, the return statement of [getMultiplier](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L245) involves a calculation of `curve[n + 1] - curve[n]`. This assumes that the curve value at index `n+1` is greater than or equal to the one at index `n`. If that is not the case, the function will revert, resulting in revert of the calling function.

The curve values are set in the following functions:
1. [__TimeLockPool_init](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L35)
2. [setCurve](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L280)
3. [setCurvePoint](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L322)

None of these functions check if the current point on curve is greater than the previous point set. 

## Impact

There are several functions which use [getMultiplier](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L233). They are:
 1. [deposit](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L85) in `TimeLockPool.sol`
 2. [extendLock](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L148) in `TimeLockPool.sol`
 3. [increaseLock](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L197) in `TimeLockPool.sol` 
 4. [fetchOldData](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/View.sol#L59) in `View.sol`
 
 Suppose the `lock duration` passed to `getMultiplier`  falls in the curve between indices `i` and `i+1`. 
 If `curve[i+1]` < `curve[i]`, then these functions will revert due to an underflow error in subtraction in [line 245](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L245) of `TimeLockPool`.

## Code Snippet
**getMultiplier function:**

```solidity
    function getMultiplier(uint256 _lockDuration) public view returns(uint256) {
        // There is no need to check _lockDuration amount, it is always checked before
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/92_
