# [C] Use after free in rusqlite

## Summary
Severity: Critical
Advisory: GHSA-8h4j-vm3r-vcq3
CVE: CVE-2020-35870
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8h4j-vm3r-vcq3
Type: github-advisory

## Affected
- crates.io: `rusqlite` — affected >=0 <0.23.0

## Details
An issue was discovered in the rusqlite crate before 0.23.0 for Rust. Memory safety can be violated via an Auxdata API use-after-free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35870
- https://github.com/rusqlite/rusqlite/commit/2ef3628dac35aeba0a97d5fb3a57746b4e1d62b3
- https://github.com/rusqlite/rusqlite
- https://github.com/rusqlite/rusqlite/releases/tag/0.23.0
- https://rustsec.org/advisories/RUSTSEC-2020-0014.html
