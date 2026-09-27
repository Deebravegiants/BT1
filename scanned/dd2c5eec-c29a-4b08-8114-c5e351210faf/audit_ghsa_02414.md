# [H] Uninitialized memory use in generator

## Summary
Severity: High
Advisory: GHSA-6c65-xcf5-299x
CVE: CVE-2019-16144
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6c65-xcf5-299x
Type: github-advisory

## Affected
- crates.io: `generator` — affected >=0 <0.6.18

## Details
An issue was discovered in the generator crate before 0.6.18 for Rust. Uninitialized memory is used by Scope, done, and yield_ during API calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16144
- https://github.com/Xudong-Huang/generator-rs/issues/11
- https://github.com/Xudong-Huang/generator-rs/issues/13
- https://github.com/Xudong-Huang/generator-rs/issues/14
- https://github.com/Xudong-Huang/generator-rs/issues/9
- https://github.com/Xudong-Huang/generator-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0020.html
