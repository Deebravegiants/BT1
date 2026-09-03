# [?] fix[ux]: fix panic in pow folding (#4996)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-05-22
Source: https://github.com/vyperlang/vyper/commit/66202171e038637e95bc550b8e36ae21054fa5f1
Type: security-commit

## Details
fix[ux]: fix panic in pow folding (#4996)

The constant-fold path for `**` in `Pow._op` calls
`math.log(decimal.Decimal(left))` to estimate whether `l**r` would
overflow `2**256` and result in a compiler hang or crash. The estimate
is only defined for `left > 1`; for any negative base it raises
`ValueError`, denying valid in-range expressions such as
`(-2) ** 2 == 4` and `(-1) ** 100 == 1`. The same math.log call also
crashes on `0 ** 0` and `1 ** N`.

Guard the heuristic with `left > 1` so degenerate bases skip the
estimate and fall through to the exact `int(left**right)` fold, which
already handles them correctly.
