# [C] Incorrect SAR implementation

## Summary
Severity: Critical
Contest weight: 0.1712
Dataset id: 16649
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The implementation of opSAR is incorrect. In case A is "negative" (sign bit is 1) the correction of the result from SHRarithBit is incorrectly done by negation (0 - A).
Counter example: sar(0x80...01, 1) gives 0xc0..01 instead of 0xc0..00:
sign(A) == 1
abs(A) == 0x7f..ff
abs(A) >> 1 == 0x3f..ff
0 - (abs(A) >> 1) == 0xc0..01
These tests should uncover the bug, but they are disabled:
[FAILED] stShift.shiftCombinations
[FAILED] stShift.shiftSignedCombinations

## Recommendation
The correct implementation of SAR in the case of A being negative would be NOT(SHR(NOT(A), D)) (A is the number to shift, D is the amount of bits to shift by), where NOT is bitwise negation, not arithmetic negation as in the current implementation.
We could use XOR and the sign bit to conditionally negate. If E contains the sign bit, then this would be (using functional and assignment notation):
MASK = SUB(0, E)
RESULT = XOR(SHR(XOR(A, MASK), D), MASK)
Polygon-Hermez: Fixed in PR #211 and test added in PR #165.
