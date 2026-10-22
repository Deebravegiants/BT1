# [H] Wrong `calcAsymmetricShare` calculation

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-vader
Published: 2021-04-28
Source: https://github.com/code-423n4/2021-04-vader-findings/issues/214
Type: code-finding

## Details
# Handle

@cmichelio


# Vulnerability details


## Vulnerability Details

The inline-comment defines the number of asymmetric shares as `(u * U * (2 * A^2 - 2 * U * u + U^2))/U^3` but the `Utils.calcAsymmetricShare` function computes `(uA * 2U^2 - 2uU + u^2) / U^3` which is not equivalent as can be seen from the `A^2` term in the first term which does not occur in the second one.
The associativity on `P * part1` is wrong, and `part2` is not multiplied by `P`.

## Impact

The math from the spec is not correctly implemented and could lead to the protocol being economically exploited, as the asymmetric share which is used to determine the collateral value in base tokens could be wrong.
For example, it might be possible to borrow more than the collateral put up.

## Recommended Mitigation Steps

Clarify if the comment is correct or the code and fix them.
