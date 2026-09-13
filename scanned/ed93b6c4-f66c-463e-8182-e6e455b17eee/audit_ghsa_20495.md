# [C] Use of Uninitialized Resource in acc_reader.

## Summary
Severity: Critical
Advisory: GHSA-799f-r78p-gq9c
CVE: CVE-2020-36513
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-799f-r78p-gq9c
Type: github-advisory

## Affected
- crates.io: `acc_reader` — affected >=0

## Details
An issue was discovered in the acc_reader crate through 2020-12-27 for Rust. read_up_to may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36513
- https://github.com/netvl/acc_reader/issues/1
- https://github.com/netvl/acc_reader
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/acc_reader/RUSTSEC-2020-0155.md
- https://rustsec.org/advisories/RUSTSEC-2020-0155.html
