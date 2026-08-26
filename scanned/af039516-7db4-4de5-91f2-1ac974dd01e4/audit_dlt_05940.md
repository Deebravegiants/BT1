# [?] fix[ux]: panic explicitly in `safe_pow()` for two-variable case (#5134)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-06-23
Source: https://github.com/vyperlang/vyper/commit/751931ff6993f2ec742a867eecb951d2229d6536
Type: security-commit

## Details
fix[ux]: panic explicitly in `safe_pow()` for two-variable case (#5134)

the else branch of `safe_pow()` (neither base nor exponent is a compile-
time constant) silently `return`ed `None`, which propagates into IR
construction in `expr.py` and would surface as a cryptic downstream
crash if the front-end guard were ever bypassed.

raise `CodegenPanic("unreachable")` instead of returning `None`,
matching the defensive `raise` style used a few lines above. the branch
is unreachable today because the type checker rejects two-variable
exponentiation with `InvalidOperation`, so mark it `# pragma: nocover`.

fixes GH 5026
