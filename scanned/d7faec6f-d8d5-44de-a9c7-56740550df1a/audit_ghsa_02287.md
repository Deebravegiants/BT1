# [C] NULL Pointer Dereference in cbox

## Summary
Severity: Critical
Advisory: GHSA-3vjm-36rr-7qrq
CVE: CVE-2020-35860
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3vjm-36rr-7qrq
Type: github-advisory

## Affected
- crates.io: `cbox` — affected >=0

## Details
An issue was discovered in the cbox crate through 2020-03-19 for Rust. The CBox API allows dereferencing raw pointers without a requirement for unsafe code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35860
- https://github.com/TomBebbington/cbox-rs/issues/2
- https://github.com/TomBebbington/cbox-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0005.html
