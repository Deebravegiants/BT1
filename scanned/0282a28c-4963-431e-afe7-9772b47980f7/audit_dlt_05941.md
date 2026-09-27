# [?] fix[codegen]: fix panic for type checking iterator types (#4767)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2025-11-04
Source: https://github.com/vyperlang/vyper/commit/a68eb5736eacb63c98db85682c1d2c123604732b
Type: security-commit

## Details
fix[codegen]: fix panic for type checking iterator types (#4767)

the type of the iterator for an array can be a supertype of the array
elements, however an assert was checking for type equivalence, which
led to panics.
