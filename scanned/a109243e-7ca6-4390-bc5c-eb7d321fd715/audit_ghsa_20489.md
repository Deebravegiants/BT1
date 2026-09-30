# [C] Use of Uninitialized Resource in binjs_io.

## Summary
Severity: Critical
Advisory: GHSA-cw4j-cf6c-mmfv
CVE: CVE-2021-45683
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-cw4j-cf6c-mmfv
Type: github-advisory

## Affected
- crates.io: `binjs_io` — affected >=0

## Details
An issue was discovered in the binjs_io crate through 2021-01-03 for Rust. The Read method may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45683
- https://github.com/binast/binjs-ref/issues/460
- https://github.com/Yoric/binjs-ref
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/binjs_io/RUSTSEC-2021-0085.md
- https://rustsec.org/advisories/RUSTSEC-2021-0085.html
