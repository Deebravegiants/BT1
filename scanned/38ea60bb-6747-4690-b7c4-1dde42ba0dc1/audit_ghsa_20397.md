# [H] Out-of-bounds Write in vec-const

## Summary
Severity: High
Advisory: GHSA-x76r-966h-5qv9
CVE: CVE-2021-45680
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-x76r-966h-5qv9
Type: github-advisory

## Affected
- crates.io: `vec-const` — affected >=0 <2.0.0

## Details
An issue was discovered in the vec-const crate before 2.0.0 for Rust. It tries to construct a Vec from a pointer to a const slice, leading to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45680
- https://github.com/Eolu/vec-const/issues/1#issuecomment-898908241
- https://github.com/Eolu/vec-const
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/vec-const/RUSTSEC-2021-0082.md
- https://rustsec.org/advisories/RUSTSEC-2021-0082.html
