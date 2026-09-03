# [?] fix: compiler was panicking when a `break` is outside of a loop (#3177)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-12-07
Source: https://github.com/vyperlang/vyper/commit/1a568bf7378e93806f22b1beb873097bc1970ad4
Type: security-commit

## Details
fix: compiler was panicking when a `break` is outside of a loop (#3177)

* fixed the compiler panicking when a break is outside of a loop

* added tests and improved test for continue

Co-authored-by: Tanguy Rocher <tanguy.rocher@protonmail.com>
