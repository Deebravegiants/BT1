# [?] fix[venom]: fix `extract32` overflow and `bytesN` clamping (#4986)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2026-05-21
Source: https://github.com/vyperlang/vyper/commit/037d31678f2f1f56c4bc69bb240bee21c8f6b34e
Type: security-commit

## Details
fix[venom]: fix `extract32` overflow and `bytesN` clamping (#4986)

Venom `extract32` had two validation gaps versus legacy codegen. The
bounds check computed `start + 32` without overflow protection — a near-
max start would wrap around to a small value, bypassing the out-of-
bounds assertion. Reuse `_assert_slice_bounds` (already used by `slice`)
which handles this correctly.

The output clamping was also incomplete: `_clamp_extract32_result` had
ad-hoc logic that didn't canonicalize `bytesN` output (dirty trailing
bytes from the 32-byte load could leak through). Legacy codegen applies
the basetype clamp for all primitive types. Consolidate all output
clamping into `clamp_basetype`, extending it to handle `BytesM_T`,
`AddressT`, `BoolT`, and 256-bit integers alongside the existing
signed/unsigned integer paths.
