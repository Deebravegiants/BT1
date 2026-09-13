# [M] Data race in may_queue

## Summary
Severity: Medium
Advisory: GHSA-pphf-f93w-gc84
CVE: CVE-2020-36217
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-pphf-f93w-gc84
Type: github-advisory

## Affected
- crates.io: `may_queue` — affected >=0

## Details
An issue was discovered in the may_queue crate through 2020-11-10 for Rust. Because Queue does not have bounds on its Send trait or Sync trait, memory corruption can occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36217
- https://github.com/Xudong-Huang/may/issues/88
- https://github.com/Xudong-Huang/may
- https://rustsec.org/advisories/RUSTSEC-2020-0111.html
