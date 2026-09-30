# [C] 5.1.5 IncorrectSARimplementation

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-rom:comparison.zkasm#L
**Description:** The implementation ofopSARis incorrect. In caseAis "negative" (sign bit is 1) the correction of the
result fromSHRarithBitis incorrectly done by negation (0 - A).
Counter example:sar(0x80...01, 1)gives0xc0..01instead of0xc0..00:
sign(A) == 1
abs(A) == 0x7f..ff
abs(A) >> 1 == 0x3f..ff
0 - (abs(A) >> 1) == 0xc0..

These tests should uncover the bug, but they are disabled:

```
[ FAILED ] stShift.shiftCombinations
[ FAILED ] stShift.shiftSignedCombinations
```
**Recommendation:** The correct implementation ofSARin the case ofAbeing negative would beNOT(SHR(NOT(A),
D))(Ais the number to shift,Dis the amount of bits to shift by), whereNOTis bitwise negation, not arithmetic
negation as in the current implementation.
We could useXORand the sign bit to conditionally negate. IfEcontains the sign bit, then this would be (using
functional and assignment notation):
MASK = SUB(0, E)
RESULT = XOR(SHR(XOR(A, MASK), D), MASK)

**Polygon-Hermez:** Fixed in PR #211 and test added in PR #165.
**Spearbit:** Acknowledged.
