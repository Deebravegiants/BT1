# [M] Cross-site Scripting in ammonia

## Summary
Severity: Medium
Advisory: GHSA-5325-xw5m-phm3
CVE: CVE-2021-38193
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5325-xw5m-phm3
Type: github-advisory

## Affected
- crates.io: `ammonia` — affected >=3.0.0 <3.1.0
- crates.io: `ammonia` — affected >=0 <2.1.3

## Details
An issue was discovered in the ammonia crate before 3.1.0 for Rust. XSS can occur because the parsing differences for HTML, SVG, and MathML are mishandled, a similar issue to CVE-2020-26870.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38193
- https://github.com/rust-ammonia/ammonia/pull/142
- https://github.com/rust-ammonia/ammonia
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ammonia/RUSTSEC-2021-0074.md
- https://rustsec.org/advisories/RUSTSEC-2021-0074.html
