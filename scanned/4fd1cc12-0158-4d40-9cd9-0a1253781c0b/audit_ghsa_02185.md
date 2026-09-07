# [C] Improper type usage in rusqlite

## Summary
Severity: Critical
Advisory: GHSA-g4w7-3qr8-5623
CVE: CVE-2020-35872
CWE: CWE-351
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g4w7-3qr8-5623
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated via the repr(Rust) type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35872
- https://github.com/rusqlite/rusqlite/commit/71b2f5187b0cbace3f8b6ff53432ff2ca0defcf0
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
