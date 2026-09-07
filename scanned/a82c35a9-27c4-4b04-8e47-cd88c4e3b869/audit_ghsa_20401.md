# [C] Use of Uninitialized Resource in messagepack-rs

## Summary
Severity: Critical
Advisory: GHSA-jwfh-j623-m97h
CVE: CVE-2021-45691
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-jwfh-j623-m97h
Type: github-advisory

## Affected
- crates.io: `messagepack-rs` — affected >=0

## Details
An issue was discovered in the messagepack-rs crate through 2021-01-26 for Rust. deserialize_string may read from uninitialized memory locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45691
- https://github.com/otake84/messagepack-rs/issues/2
- https://github.com/otake84/messagepack-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/messagepack-rs/RUSTSEC-2021-0092.md
- https://rustsec.org/advisories/RUSTSEC-2021-0092.html
