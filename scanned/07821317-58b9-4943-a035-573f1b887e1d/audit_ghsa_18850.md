# [H] binary_vec_io access memory out-of-bounds in binary_read_to_ref and binary_write_from_ref

## Summary
Severity: High
Advisory: GHSA-wwxp-hxh6-8gf8
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-wwxp-hxh6-8gf8
Type: github-advisory

## Affected
- crates.io: `binary_vec_io` — affected >=0

## Details
Safe functions accept a single `&T` or `&mut T` but multiply by `n` to create slices extending beyond allocated memory when `n > 1`.

These functions use `from_raw_parts` to create slices larger than the underlying allocation, violating memory safety.

The binary_vec_io repository is archived and unmaintained.

## References
- https://github.com/RustSec/advisory-db/pull/2428
- https://gist.github.com/lewismosciski/57ac3b8b7a861abdd0d7ae6f39de5a9d
- https://github.com/10XGenomics/rust-toolbox
- https://rustsec.org/advisories/RUSTSEC-2025-0109.html
