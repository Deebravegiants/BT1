# [M] Excessive Indirection

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/Exponential.sol
Type: audit-issue

## Details
The [Exponential contract](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/Exponential.sol) represents a fixed-size decimal number with a `uint` that is scaled up so the smallest non-zero decimal value is internally represented by the number 1\. However, it is also unnecessarily wrapped in a struct.

This has the advantage that the scaled values can have a unique Solidity type. On the other hand, this feature is used inconsistently throughout the code base and introduces a very large overhead. Many of the functions in the `Exponential` contract implement common mathematical operations on the `Exp` type when the equivalent functions already exist for the `uint256` type. Most of the functions in the `Exponential` contract could be simplified or eliminated if the additional layer of indirection were removed. Additionally, many operations are complicated by mapping back and forth between the two representations.

Consider using the `uint256` type to internally represent the fixed-size decimal numbers. Then, consider enforcing the existing `Mantissa` suffix convention to consistently indicate whether a given variable is scaled.
