# [H] Data races in rusqlite

## Summary
Severity: High
Advisory: GHSA-rjh8-p66p-jrh5
CVE: CVE-2020-35871
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rjh8-p66p-jrh5
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated via an Auxdata API data race.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35871
- https://github.com/rusqlite/rusqlite/commit/2ef3628dac35aeba0a97d5fb3a57746b4e1d62b3
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
