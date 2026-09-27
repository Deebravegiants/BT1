# [H] Double free in insert_many

## Summary
Severity: High
Advisory: GHSA-29hg-r7c7-54fr
CVE: CVE-2021-29933
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-29hg-r7c7-54fr
Type: github-advisory

## Affected
- crates.io: `insert_many` — affected >=0

## Details
An issue was discovered in the insert_many crate through 2021-01-26 for Rust. Elements may be dropped twice if a .next() method panics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29933
- https://github.com/rphmeier/insert_many/issues/1
- https://github.com/rphmeier/insert_many
- https://rustsec.org/advisories/RUSTSEC-2021-0042.html
