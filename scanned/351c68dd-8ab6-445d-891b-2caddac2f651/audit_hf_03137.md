# [M] Curve points should be guaranteed to be mono-

## Summary
Severity: Medium
Contest weight: 0.3920
Dataset id: 17623
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lack of checks to ensure the points in the curve are monotonic increasing, which can result in a malfunction of deposit() / extendLock() due to underflow when the curve is not set properly.  
In the current implementation, getMultiplier() assume the later point in the curve is always bigger than the previous point, otherwise curve[n+1] - curve[n] will revert due to underflow.  
However, since there is no check in __TimeLockPool_init() / setCurve() / setCurvePoint() to guarantee that, a lower point can actually be set after a higher point.  
deposit() / extendLock() may revert due to underflow.

## Recommendation
Consider adding a new internal function to validate the curve points:  
```solidity
function checkCurve(uint256[] calldata _curve) internal {
    if (_curve.length < 2) {
        revert ShortCurveError();
    }
    for (uint256 i; i < _curve.length - 1; ++i) {
        if (
            _curve[i + 1] < _curve[i]
        ) {
            revert CurveIncreaseError();
        }
    }
}
```
