# [H] EDPU-1 | Adjusting Long and Short Token Amounts Incorrect

## Summary
Severity: High
Contest weight: 0.2345
Dataset id: 18171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In several cases the getAdjustedLongAndShortTokenAmounts function reverts or returns a nonsensical result: 1) poolLongTokenAmount and poolShortTokenAmount access the pool amount for the same token as longToken and shortToken are the same. As a result, the pool amounts are equal and the else case will always be entered. 2) On line 387, when uint256 diff = poolLongTokenAmount - poolShortTokenAmount is performed, the larger value is always subtracted from the smaller value causing underflow. 3) On line 396, when uint256 diff = poolShortTokenAmount - poolLongTokenAmount is performed, the larger or equal value is being subtracted from the smaller value which will underflow in most cases. 4) On line 400, adjustedLongTokenAmount - longTokenAmount - adjustedShortTokenAmount does not set the adjustedLongTokenAmount but rather computes the result of subtraction.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/EDPU_1.ts

## Recommendation
Refactor the getAdjustedLongAndShortTokenAmounts function to address the above problems.
