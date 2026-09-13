# [C] Out of bounds read in Ozone

## Summary
Severity: Critical
Advisory: GHSA-p2q9-9cq6-h3jw
CVE: CVE-2020-35877
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-p2q9-9cq6-h3jw
Type: github-advisory

## Affected
- crates.io: `ozone` — affected >=0

## Details
An issue was discovered in the ozone crate through version 0.1.0 for Rust. Memory safety is violated because of out-of-bounds access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35877
- https://github.com/bqv/ozone
- https://rustsec.org/advisories/RUSTSEC-2020-0022.html
