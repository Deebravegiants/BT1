# [H] Free of uninitialized memory in autorand

## Summary
Severity: High
Advisory: GHSA-cgmg-2v6m-fjg7
CVE: CVE-2020-36210
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cgmg-2v6m-fjg7
Type: github-advisory

## Affected
- crates.io: `autorand` — affected >=0 <0.2.3

## Details
An issue was discovered in the autorand crate before 0.2.3 for Rust. Because of impl Random on arrays, uninitialized memory can be dropped when a panic occurs, leading to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36210
- https://github.com/mersinvald/autorand-rs/issues/5
- https://github.com/mersinvald/autorand-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0103.html
