# [C] Drop of uninitialized memory in Ozone

## Summary
Severity: Critical
Advisory: GHSA-m3ww-7hrp-gw9w
CVE: CVE-2020-35878
CWE: CWE-119, CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m3ww-7hrp-gw9w
Type: github-advisory

## Affected
- crates.io: `ozone` — affected >=0

## Details
An issue was discovered in the ozone crate through version 0.1.0 for Rust. Memory safety is violated because of the dropping of uninitialized memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35878
- https://github.com/bqv/ozone
- https://rustsec.org/advisories/RUSTSEC-2020-0022.html
