# [H] Missing Initialization of Resource in pnet

## Summary
Severity: High
Advisory: GHSA-24g6-5rx7-58wj
CVE: CVE-2019-25054
CWE: CWE-909
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-24g6-5rx7-58wj
Type: github-advisory

## Affected
- crates.io: `pnet` — affected >=0 <0.27.2

## Details
An issue was discovered in the pnet crate before 0.27.2 for Rust. There is a segmentation fault (upon attempted dereference of an uninitialized descriptor) because of an erroneous IcmpTransportChannelIterator compiler optimization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25054
- https://github.com/libpnet/libpnet/issues/449
- https://github.com/libpnet/libpnet
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/pnet/RUSTSEC-2019-0037.md
- https://rustsec.org/advisories/RUSTSEC-2019-0037.html
