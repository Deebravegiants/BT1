# [C] Data races in rusqlite

## Summary
Severity: Critical
Advisory: GHSA-6q5w-m3c5-rv95
CVE: CVE-2020-35866
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6q5w-m3c5-rv95
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated via VTab / VTabCursor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35866
- https://github.com/rusqlite/rusqlite/commit/c9ef5bd63cad5c0c123344c072b490a1a9bcbe1f
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
