# [H] Use of Uninitialized Resource in bite.

## Summary
Severity: High
Advisory: GHSA-v2ch-fc8f-qm33
CVE: CVE-2020-36511
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-v2ch-fc8f-qm33
Type: github-advisory

## Affected
- crates.io: `bite` — affected >=0

## Details
An issue was discovered in the bite crate through 2020-12-31 for Rust. read::BiteReadExpandedExt::read_framed_max may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36511
- https://github.com/hinaria/bite/issues/1
- https://github.com/hinaria/bite
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/bite/RUSTSEC-2020-0153.md
- https://rustsec.org/advisories/RUSTSEC-2020-0153.html
