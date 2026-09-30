# [M] boundedSub() might fail to return the result due to incorrect underflow check

## Summary
Severity: Medium
Contest weight: 0.4723
Dataset id: 19858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The goal of boundedSub() is to bound the result regardless what the inputs are to prevent overflows/underflows. However, the goal is not achieved for some cases.
As a result, boundedSub() still might underflow and still might revert. The goal of the function is not achieved.
As a result, the protocol might not be fault-tolerant as it is supposed to be - when boundedSub() is designed to not revert in any case, it still might revert. For example, function MarketUtils.getNextFundingAmountPerSize() will be affected.
boundedSub() is designed to always bound its result between type(int256).min and type(int256).max so that it will never overflow/underflow:
cts/utils/Calc.sol#L116-L135
It achieves its goal in three cases:
1) Case 1: if either a or b is zero or the signs are the same there should not be any overflow.
2) Case 2: a > 0, and b < 0, and a-b > type(int256).max, then we need to return type(int256).max.
3) Case 3: a < 0, and b > 0, and a - b < type(int256).min, then we need to return type(int256).min which essentially is checking a < 0 && b + a <= type(int256).min, a wrong condition to check. Because of using this wrong condition, underflow cases will not be detected and the function will revert instead of returning type(int256).min in this case.
To verify, suppose a = type(int256).min and b = 1, a-b needs to be bounded to prevent underflow and the function should have returned type(int256).min.
However, the function will fail the condition, as a result, it will not execute the if return a - b;
As a result, instead of returning the minimum, the function will revert in the last line due to underflow. This violates the property of the function: it should have returned the bounded result type(int256).min and should not have reverted in any case.
The following POC in Remix can show that the following function will revert:
```solidity
function testBoundedSub() public pure returns (int256){
return boundedSub(type(int256).min+3, 4);
}
```
boundedSub() does not guarantee underflow/overflow free as it is designed to be.
As a result, the protocol might break at points when it is not supposed to break. For example, function MarketUtils.getNextFundingAmountPerSize() will be affected.

## Recommendation
```diff
The correction is as follows:
function boundedSub(int256 a, int256 b) internal pure returns (int256) {
// if either a or b is zero or the signs are the same there should not
be any overflow
if (a == 0 || b == 0 || (a > 0 && b > 0) || (a < 0 && b < 0)) {
return a - b;
}
// if adding `-b` to `a` would result in a value greater than the max
int256 value
// then return the max int256 value
if (a > 0 && -b >= type(int256).max - a) {
return type(int256).max;
}
// if subtracting `b` from `a` would result in a value less than the min
int256 value
// then return the min int256 value
- if (a < 0 && b <= type(int256).min - a) {
+ if (a < 0 && a <= type(int256).min + b) {
return type(int256).min;
}
return a - b;
}
```
