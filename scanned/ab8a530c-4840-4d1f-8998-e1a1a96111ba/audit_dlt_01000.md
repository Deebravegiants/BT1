# [?] fix[codegen]: overflow check in `slice()` (#3818)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-03-21
Source: https://github.com/vyperlang/vyper/commit/f8d4b97ab91ec14ac55911fd0aee5eec7def0fa8
Type: security-commit

## Details
fix[codegen]: overflow check in `slice()` (#3818)

the buffer out-of-bounds check in slice() does not take into account the
possibility for arithmetic overflow. this commit fixes the oob check by
adding an overflow check. it also refactors the slice check into a
helper function, and adds relevant tests.

patches GHSA-9x7f-gwxq-6f2c.
---------

Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>
