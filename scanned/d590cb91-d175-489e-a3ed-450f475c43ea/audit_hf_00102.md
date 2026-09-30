# [M] M-1 Possible arithmetic overﬂow

## Summary
Severity: Medium
Contest weight: 0.0886
Dataset id: 195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the line UserAccounting.sol#L29 the number with the type int256 is converted to the number with the type uint256. The number is taken with a minus sign.
But before that, there is no check that the number is less than 0.
If we take a small positive value and apply the transformation uint256(-amount) to it, we get a very large value due to arithmetic overﬂow.
For example, if you take number 1000, then after conversion you get value 115792089237316195423570985008687907853269984665640564039457584007913129638936.

## Recommendation
Before line 29 you need to check if the value of the variable is not less than 0.
If the value of the variable is positive, then do not do the conversion.
