# [?] fix[lang]: filter oob array access during folding (#4571)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2025-04-12
Source: https://github.com/vyperlang/vyper/commit/2d515d3b34097b05ee3bc9c6eaee3682f166cbd3
Type: security-commit

## Details
fix[lang]: filter oob array access during folding (#4571)

constant folding was not filtering out oob array index accesses. this is
because it was raising `UnfoldableNode`, which is caught by the folding
machinery. this commit changes it to an `ArrayIndexException`, which
will propagate to the user and abort compilation.

---------

Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>
