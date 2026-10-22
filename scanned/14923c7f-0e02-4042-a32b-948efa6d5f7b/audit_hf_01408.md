# [H] pow function silently overflows and yields wrong results

## Summary
Severity: High
Contest weight: 0.1906
Dataset id: 7221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FixedPointMath.pow function can silently overflow in the intermediate computation of ylnx := mul(y_int256, lnx). The final result will be wrong.
function test_pow() public {
    uint256 x = 2e18;
    // computes y * ln(x) first with x,y 18-decimal fixed point
    // chosen s.t. y * ln(x) overflows and is close to 0
    uint256 y = type(uint256).max / uint256(FixedPointMath.ln(int256(x))) + 1;
    // 2.0 ** y should be a huge value but is 1.0 (1e18) as y*ln(x) overflows and then computes exp(0) = 1e18
    uint256 res = FixedPointMath.pow(x, y);
    assertEq(res, 1e18); // this should not be true but is
}
This function is used by several computations in HyperdriveMath.sol and YieldSpaceMath.sol.

## Recommendation
First, there are unsafe typecasts in the functions (like y_int256) that should be safe typecasts.
The ylnx multiplication should be checked to have not overflown.
