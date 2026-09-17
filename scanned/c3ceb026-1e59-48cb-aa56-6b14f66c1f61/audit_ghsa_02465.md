# [C] Data race in internment

## Summary
Severity: Critical
Advisory: GHSA-gppw-3h6h-v6q2
CVE: CVE-2021-28037
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gppw-3h6h-v6q2
Type: github-advisory

## Affected
- crates.io: `internment` — affected >=0 <0.4.2

## Details
An issue was discovered in the internment crate before 0.4.2 for Rust. There is a data race that can cause memory corruption because of the unconditional implementation of Sync for Intern<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28037
- https://github.com/droundy/internment/issues/20
- https://github.com/droundy/internment
- https://rustsec.org/advisories/RUSTSEC-2021-0036.html
