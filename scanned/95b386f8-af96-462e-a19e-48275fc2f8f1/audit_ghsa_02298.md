# [M] Cross site scripting in comrak

## Summary
Severity: Medium
Advisory: GHSA-xmr7-v725-2jjr
CVE: CVE-2021-27671
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-xmr7-v725-2jjr
Type: github-advisory

## Affected
- crates.io: `comrak` — affected >=0 <0.9.1

## Details
An issue was discovered in the comrak crate before 0.9.1 for Rust. Cross site scripting (XSS) can occur because the protection mechanism for data: and javascript: URIs is case-sensitive, allowing (for example) Data: to be used in an attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27671
- https://github.com/kivikakk/comrak/commit/b3efbb6e427bcd33bb14db45753ad4fd98e0f5bf
- https://github.com/kivikakk/comrak
- https://github.com/kivikakk/comrak/releases/tag/0.9.1
- https://rustsec.org/advisories/RUSTSEC-2021-0026.html
