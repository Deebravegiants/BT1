# [H]  Use of Uninitialized Resource in truetype

## Summary
Severity: High
Advisory: GHSA-v7q4-97x4-4qw2
CVE: CVE-2021-28030
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-v7q4-97x4-4qw2
Type: github-advisory

## Affected
- crates.io: `truetype` — affected >=0 <0.30.1

## Details
An issue was discovered in the truetype crate before 0.30.1 for Rust. Attackers can read the contents of uninitialized memory locations via a user-provided Read operation within Tape::take_bytes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28030
- https://github.com/bodoni/truetype/issues/11
- https://github.com/bodoni/truetype
- https://rustsec.org/advisories/RUSTSEC-2021-0029.html
