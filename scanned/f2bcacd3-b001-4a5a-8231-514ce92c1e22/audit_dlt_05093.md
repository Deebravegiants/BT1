# [?] fix(polynomials): avoid out-of-bounds intermediate pointer in token-indexed accessors

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-25
Source: https://github.com/AztecProtocol/aztec-packages/commit/0ccc236fe4492a2f9e3e50d659677ad342b1baef
Type: security-commit

## Details
fix(polynomials): avoid out-of-bounds intermediate pointer in token-indexed accessors

The token-indexed proxies and operator[] overloads formed `data() - start_index() + base`
(and `gather/scatter(data() - start_index(), idx)`). When start_index > 0 the intermediate
`data() - start_index()` points before the backing array, which is UB per [expr.add]/4 even
though the final address lands back in-bounds. Rewrite the contiguous paths as
`data() + (base - start_index())` (integer subtraction first) and the gather/scatter paths to
pass `data()` with indices rebased by start_index (new rebase_lane_indices helper), keeping every
in-flight pointer inside the array.
