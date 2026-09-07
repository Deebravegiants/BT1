# [C] Out of bounds write in traitobject

## Summary
Severity: Critical
Advisory: GHSA-j79j-cx3h-g27h
CVE: CVE-2020-35881
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j79j-cx3h-g27h
Type: github-advisory

## Affected
- crates.io: `traitobject` — affected >=0

## Details
An issue was discovered in the traitobject crate through 2020-06-01 for Rust. It has false expectations about fat pointers, possibly causing memory corruption in, for example, Rust 2.x.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35881
- https://github.com/reem/rust-traitobject/issues/7
- https://github.com/reem/rust-traitobject
- https://rustsec.org/advisories/RUSTSEC-2020-0027.html
