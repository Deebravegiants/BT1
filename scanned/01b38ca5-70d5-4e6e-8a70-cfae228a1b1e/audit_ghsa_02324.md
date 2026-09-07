# [C] Out of bounds read in fltk

## Summary
Severity: Critical
Advisory: GHSA-vjmg-pc8h-p6p8
CVE: CVE-2021-28308
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vjmg-pc8h-p6p8
Type: github-advisory

## Affected
- crates.io: `fltk` — affected >=0 <0.15.3

## Details
An issue was discovered in the fltk crate before 0.15.3 for Rust. There is an out-of bounds read because the pixmap constructor lacks pixmap input validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28308
- https://github.com/MoAlyousef/fltk-rs/issues/519
- https://github.com/MoAlyousef/fltk-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0038.html
