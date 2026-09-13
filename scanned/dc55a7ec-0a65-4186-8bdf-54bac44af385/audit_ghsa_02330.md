# [C] Free of uninitialized memory in adtensor

## Summary
Severity: Critical
Advisory: GHSA-rg4m-gww5-7p47
CVE: CVE-2021-29936
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rg4m-gww5-7p47
Type: github-advisory

## Affected
- crates.io: `adtensor` — affected >=0

## Details
An issue was discovered in the adtensor crate through 0.0.3 for Rust. There is a drop of uninitialized memory via the FromIterator implementation for Vector and Matrix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29936
- https://github.com/charles-r-earp/adtensor/issues/4
- https://github.com/charles-r-earp/adtensor
- https://rustsec.org/advisories/RUSTSEC-2021-0045.html
