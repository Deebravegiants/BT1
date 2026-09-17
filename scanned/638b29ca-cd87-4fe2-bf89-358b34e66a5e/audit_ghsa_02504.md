# [C] Double free in http

## Summary
Severity: Critical
Advisory: GHSA-6rhx-hqxm-8p36
CVE: CVE-2019-25009
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6rhx-hqxm-8p36
Type: github-advisory

## Affected
- crates.io: `http` — affected >=0 <0.1.20

## Details
An issue was discovered in the http crate before 0.1.20 for Rust. The HeaderMap::Drain API can use a raw pointer, defeating soundness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25009
- https://rustsec.org/advisories/RUSTSEC-2019-0034.html
