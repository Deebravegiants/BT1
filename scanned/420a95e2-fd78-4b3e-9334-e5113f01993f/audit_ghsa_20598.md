# [H] Window may read from uninitialized memory locations in rdiff

## Summary
Severity: High
Advisory: GHSA-2rxc-8f9w-fjq8
CVE: CVE-2021-45694
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-2rxc-8f9w-fjq8
Type: github-advisory

## Affected
- crates.io: `rdiff` — affected >=0

## Details
An issue was discovered in the rdiff crate through version 0.1.2 for Rust. Window may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45694
- https://github.com/dyule/rdiff/issues/3
- https://github.com/dyule/rdiff
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/rdiff/RUSTSEC-2021-0094.md
- https://rustsec.org/advisories/RUSTSEC-2021-0094.html
