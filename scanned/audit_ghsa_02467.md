# [C] Mishandling of format strings in rusqlite

## Summary
Severity: Critical
Advisory: GHSA-8r7q-r9mx-35rh
CVE: CVE-2020-35869
CWE: CWE-134
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8r7q-r9mx-35rh
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated because rusqlite::trace::log mishandles format strings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35869
- https://github.com/rusqlite/rusqlite/commit/2327d3b774927fdf48903c0bdc1ca7ec93c7c8d0
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
