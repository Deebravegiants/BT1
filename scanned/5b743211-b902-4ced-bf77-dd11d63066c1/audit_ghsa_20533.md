# [H] Panic mishandled in libpulse-binding

## Summary
Severity: High
Advisory: GHSA-xvcg-2q82-r87j
CVE: CVE-2019-25055
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-xvcg-2q82-r87j
Type: github-advisory

## Affected
- crates.io: `libpulse-binding` — affected >=0 <2.6.0

## Details
An issue was discovered in the libpulse-binding crate before 2.6.0 for Rust. It mishandles a panic that crosses a Foreign Function Interface (FFI) boundary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25055
- https://github.com/jnqnfe/pulse-binding-rust/commit/7fd282aef7787577c385aed88cb25d004b85f494
- https://github.com/jnqnfe/pulse-binding-rust
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/libpulse-binding/RUSTSEC-2019-0038.md
- https://rustsec.org/advisories/RUSTSEC-2019-0038.html
