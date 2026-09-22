# [C] Use of Uninitialized Resource in bronzedb-protocol.

## Summary
Severity: Critical
Advisory: GHSA-jv2r-jx6q-89jg
CVE: CVE-2021-45682
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-jv2r-jx6q-89jg
Type: github-advisory

## Affected
- crates.io: `bronzedb-protocol` — affected >=0

## Details
An issue was discovered in the bronzedb-protocol crate through 2021-01-03 for Rust. ReadKVExt may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45682
- https://github.com/Hexilee/BronzeDB/issues/1
- https://github.com/Hexilee/BronzeDB
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/bronzedb-protocol/RUSTSEC-2021-0084.md
- https://rustsec.org/advisories/RUSTSEC-2021-0084.html
