# [M] Data races in thex

## Summary
Severity: Medium
Advisory: GHSA-j42v-6wpm-r847
CVE: CVE-2020-35927
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-j42v-6wpm-r847
Type: github-advisory

## Affected
- crates.io: `thex` — affected >=0

## Details
An issue was discovered in the thex crate through 2020-12-08 for Rust. Thex<T> allows cross-thread data races of non-Send types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35927
- https://rustsec.org/advisories/RUSTSEC-2020-0090.html
