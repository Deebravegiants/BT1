# [M] Curve points are not validated to be continuously increasing

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/47
Type: sherlock-finding

## Details
berndartmueller

medium

# Curve points are not validated to be continuously increasing

## Summary

Curve points are not validated to be continuously increasing and in case a curve point is less than its predecessor, the `getMultiplier` function will revert

## Vulnerability Detail

Curve points are set by governance in multiple places. Each point on the curve is expected to be greater than the previous point. However, this is not validated in the code. If a point is set to a value less than the previous point, the linear interpolation in `TimeLockPool.getMultiplier` will revert due to `curve[n + 1]` < `curve[n]`.

## Impact

The core functionality of the `TimeLockPool` contract will be broken and will revert until the curve is fixed by governance.

## Code Snippet

[TimeLockPool.sol#L245](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L245)

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
    return 1e18 + curve[n] + (_lockDuration - n * unit) * (curve[n + 1] - curve[n]) / unit; // @audit-info Can revert due to `curve[n + 1] - curve[n]`
}
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/47_
