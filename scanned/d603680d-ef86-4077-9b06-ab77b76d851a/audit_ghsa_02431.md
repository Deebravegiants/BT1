# [C] Read of uninitialized memory in cdr

## Summary
Severity: Critical
Advisory: GHSA-37jj-wp7g-7wj4
CVE: CVE-2021-26305
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-37jj-wp7g-7wj4
Type: github-advisory

## Affected
- crates.io: `cdr` — affected >=0 <0.2.4

## Details
An issue was discovered in Deserializer::read_vec in the cdr crate before 0.2.4 for Rust. A user-provided Read implementation can gain access to the old contents of newly allocated heap memory, violating soundness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26305
- https://github.com/hrektts/cdr-rs/issues/10
- https://github.com/hrektts/cdr-rs/pull/11
- https://github.com/hrektts/cdr-rs/commit/0e6006de464caa331643f86cd2d9ba3b32b09833
- https://github.com/hrektts/cdr-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0012.html
