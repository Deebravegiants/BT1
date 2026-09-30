# [H] Memory safety violation in crayon

## Summary
Severity: High
Advisory: GHSA-m833-jv95-mfjh
CVE: CVE-2020-35889
CWE: CWE-367
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m833-jv95-mfjh
Type: github-advisory

## Affected
- crates.io: `crayon` — affected >=0

## Details
An issue was discovered in the crayon crate through 2020-08-31 for Rust. A TOCTOU issue has a resultant memory safety violation via HandleLike.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35889
- https://github.com/shawnscode/crayon/issues/87
- https://github.com/shawnscode/crayon
- https://rustsec.org/advisories/RUSTSEC-2020-0037.html
