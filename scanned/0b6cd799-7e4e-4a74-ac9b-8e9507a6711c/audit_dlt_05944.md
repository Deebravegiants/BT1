# [?] fix[lang]: fix panic in call cycle detection (#4200)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-08-07
Source: https://github.com/vyperlang/vyper/commit/9b322d651cd5fb431e208b079382ce94fe82abd9
Type: security-commit

## Details
fix[lang]: fix panic in call cycle detection (#4200)

fix cycle detection in `_compute_reachable_set()` by adding a check for
subcycles in the current call path

the function was detecting cycles by checking for a cyclic call to the
*root* of the call path

if the cycle was within the call path (excluding the root) it could
fall into infinite recursion.
