# [C] Data races in rusqlite

## Summary
Severity: Critical
Advisory: GHSA-3cgf-9m6x-pwwr
CVE: CVE-2020-35868
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3cgf-9m6x-pwwr
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated via UnlockNotification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35868
- https://github.com/rusqlite/rusqlite/commit/45fd77ee43c38eea4d6f4e2e56c1667a55ec654f
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
