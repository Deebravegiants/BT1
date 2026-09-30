# [H] scaly: Multiple soundness issues in Rust safe APIs

## Summary
Severity: High
Advisory: GHSA-2c6h-4899-wjxr
CWE: CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-2c6h-4899-wjxr
Type: github-advisory

## Affected
- crates.io: `scaly` — affected >=0

## Details
Affected versions contain multiple safe APIs that can trigger undefined behavior:

- `Array<T>::index` can perform an out-of-bounds read.
- `String::get_length` can perform an out-of-bounds read.
- `String::append_character` can perform an invalid write.
- `String::to_c_string` can perform an out-of-bounds write.

These issues were reproduced against `scaly` 0.0.37 under Miri. The crate is unmaintained.

## References
- https://github.com/rustsec/advisory-db/issues/2594
- https://github.com/rschleitzer/Scaly
- https://rustsec.org/advisories/RUSTSEC-2026-0080.html
