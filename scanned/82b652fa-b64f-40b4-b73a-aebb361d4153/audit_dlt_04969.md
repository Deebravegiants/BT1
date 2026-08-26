# [M] Possible DOS in `deposit()`, `extendLock()` and `increaseLock()` because of potential overflow

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/72
Type: sherlock-finding

## Details
minhquanym

medium

# Possible DOS in `deposit()`, `extendLock()` and `increaseLock()` because of potential overflow

## Summary
The functions `deposit()`, `extendLock()` and `increaseLock()` are vulnerable to DOS because they use function `getMultiplier()` and it can be overflow.
https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L245

## Vulnerability Detail
The function `getMultiplier()` calculates the multiplier from the curve given the duration. The formula uses `curve[n + 1] - curve[n]` and it can be overflow or divided by zero error. 
- In case `curve[n + 1] == curve[n]`, it will be reverted because of division by zero.
- In case `curve[n + 1] < curve[n]`, it will be reverted because of underflow.
In both cases, these 3 function that make use of `getMultiplier()` will be reverted too.

## Impact
Users cannot deposit, extend or increase their lock because of denial-of-service.

## Code Snippet
The last formula in function `getMultiplier()` can be reverted.
```solidity
function getMultiplier(uint256 _lockDuration) public view returns(uint256) {
    // There is no need to check _lockDuration amount, it is always checked before
    // in the functions that call this function

    // n is the time unit where the lockDuration stands
    uint n = _lockDuration / unit;
    // if last point no need to interpolate
    // trim de curve if it exceedes the maxBonus // TODO check if this is needed
    if (n == curve.length - 1) {
        return 1e18 + curve[n];
    }
    // linear interpolation between points
    return 1e18 + curve[n] + (_lockDuration - n * unit) * (curve[n + 1] - curve[n]) / unit;
}
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/72_
