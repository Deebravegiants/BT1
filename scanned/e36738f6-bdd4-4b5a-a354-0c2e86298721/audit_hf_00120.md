# [H] Wrong `calcAsymmetricShare` calculation

## Summary
Severity: High
Contest weight: 0.2174
Dataset id: 282
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The inline-comment defines the number of asymmetric shares as `(u * U * (2 * A^2 - 2 * U * u + U^2))/U^3` but the `Utils.calcAsymmetricShare` function computes `(uA * 2U^2 - 2uU + u^2) / U^3` which is not equivalent as can be seen from the `A^2` term in the first term which does not occur in the second one.

The associativity on `P * part1` is wrong, and `part2` is not multiplied by `P`.

The math from the spec is not correctly implemented and could lead to the protocol being economically exploited, as the asymmetric share (which is used to determine the collateral value in base tokens) could be wrong. For example, it might be possible to borrow more than the collateral put up.

Recommend clarifying if the comment or the code is correct and fix them if not.

Valid

Whilst the math is incorrect, in the current implementation it is not yet implemented, so disagree with Severity (funds not lost), recommend: 2

## Recommendation
No recommendation
