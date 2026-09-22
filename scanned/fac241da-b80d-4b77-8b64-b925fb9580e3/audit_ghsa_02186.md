# [H] Command injection in kekbit

## Summary
Severity: High
Advisory: GHSA-g83m-67wh-whpw
CVE: CVE-2020-36449
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g83m-67wh-whpw
Type: github-advisory

## Affected
- crates.io: `kekbit` — affected >=0 <0.3.4

## Details
An issue was discovered in the kekbit crate before 0.3.4 for Rust. For ShmWriter<H>, Send is implemented without requiring H: Send.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36449
- https://github.com/motoras/kekbit/issues/34
- https://github.com/motoras/kekbit
- https://rustsec.org/advisories/RUSTSEC-2020-0129.html
