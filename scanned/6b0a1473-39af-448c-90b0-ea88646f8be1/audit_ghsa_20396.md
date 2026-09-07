# [H] Out-of-bounds Write in derive-com-impl

## Summary
Severity: High
Advisory: GHSA-w4cc-pc2h-whcj
CVE: CVE-2021-45681
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-w4cc-pc2h-whcj
Type: github-advisory

## Affected
- crates.io: `derive-com-impl` — affected >=0

## Details
An issue was discovered in the derive-com-impl crate before 0.1.2 for Rust. An invalid reference (and memory corruption) can occur because AddRef might not be called before returning a pointer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45681
- https://github.com/Connicpu/com-impl/issues/1
- https://github.com/connicpu/com-impl
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/derive-com-impl/RUSTSEC-2021-0083.md
- https://rustsec.org/advisories/RUSTSEC-2021-0083.html
