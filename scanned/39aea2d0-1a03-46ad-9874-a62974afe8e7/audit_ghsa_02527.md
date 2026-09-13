# [H] Data races in aovec

## Summary
Severity: High
Advisory: GHSA-g489-xrw3-3v8w
CVE: CVE-2020-36207
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g489-xrw3-3v8w
Type: github-advisory

## Affected
- crates.io: `aovec` — affected >=0

## Details
An issue was discovered in the aovec crate through 2020-12-10 for Rust. Because Aovec<T> does not have bounds on its Send trait or Sync trait, a data race and memory corruption can occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36207
- https://github.com/krl/aovec
- https://rustsec.org/advisories/RUSTSEC-2020-0099.html
