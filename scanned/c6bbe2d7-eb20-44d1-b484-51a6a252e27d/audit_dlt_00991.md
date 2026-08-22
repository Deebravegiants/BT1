# [?] fix[ux]: fix false positive for overflow in type checker (#4385)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-12-09
Source: https://github.com/vyperlang/vyper/commit/12ab4919cc4618fcac4f5d24d45a0e7fdbc4a48c
Type: security-commit

## Details
fix[ux]: fix false positive for overflow in type checker (#4385)

this commit fixes a false positive for integer overflow in
the typechecker involving nested pow operations by filtering
`OverflowException` in `_validate_op`. the previous code assumed that
`validate_numeric_op` could throw anything besides `InvalidOperation`,
but for the `Pow` binop, it can throw `OverflowException`.

---------

Co-authored-by: Charles Cooper <cooper.charles.m@gmail.com>
