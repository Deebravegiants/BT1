# [M] ATPH-2 | Half Rounding Improperly Handles 0 Quotient

## Summary
Severity: Medium
Contest weight: 0.1191
Dataset id: 19359
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Orderly utilizes the halfUp and halfDown methods to round the quotient up or down on the magnitude of the fractional part. However, the edge case of a 0 quotient will cause the division to return a mathematically incorrect result. For example, consider the function call halfUp16_8(10, 11) int256 quotient = dividend / divisor = 10 / 11 = 0 int256 remainder = dividend % divisor = 10 % 11 = 10 if (10 * 2 >= 11) { if (quotient > 0) { quotient += 1; } else { quotient -= 1; <- quotient = 0 - 1 = -1 } } The returned quotient is -1 although 10 / 11 = 0.909 is not supposed to be a negative number and should round to 1.

## Proof of Concept
https://github.com/GuardianAudits/OrderlyEVMContractsSuite/blob/4e216c2befe63c5379059f9359a7b3a0da008a71/test/GuardianPOC.t.sol#L523

## Recommendation
Add 1 to the quotient when quotient >= 0
