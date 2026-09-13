# [M] Out of bounds read in lazy-init

## Summary
Severity: Medium
Advisory: GHSA-w47j-hqpf-qw9w
CVE: CVE-2021-25901
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w47j-hqpf-qw9w
Type: github-advisory

## Affected
- crates.io: `lazy-init` — affected >=0 <0.4.0

## Details
An issue was discovered in the lazy-init crate through 2021-01-17 for Rust. Lazy lacks a Send bound, leading to a data race.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25901
- https://github.com/khuey/lazy-init/issues/9
- https://github.com/khuey/lazy-init
- https://rustsec.org/advisories/RUSTSEC-2021-0004.html
