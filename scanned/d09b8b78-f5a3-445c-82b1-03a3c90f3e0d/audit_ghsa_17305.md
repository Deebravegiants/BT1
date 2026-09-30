# [M] ruint affected by unsoundness of safe `reciprocal_mg10`

## Summary
Severity: Medium
Advisory: GHSA-9fjq-45qv-pcm7
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-9fjq-45qv-pcm7
Type: github-advisory

## Affected
- crates.io: `ruint` — affected >=0

## Details
The function `reciprocal_mg10` is marked as safe but can trigger undefined behavior (out-of-bounds access) because it relies on `debug_assert!` for safety checks instead of `assert!`.

When compiled in release mode, the `debug_assert!` is optimized out, potentially allowing invalid inputs to cause memory corruption.

## References
- https://github.com/recmo/uint/issues/550
- https://github.com/recmo/uint
- https://github.com/recmo/uint/blob/17c9b3e9062f74a39701e68dec358375595d33d7/src/algorithms/div/reciprocal.rs#L79-L87
- https://rustsec.org/advisories/RUSTSEC-2025-0137.html
