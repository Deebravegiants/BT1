# [H] Use After Free in tremor-script

## Summary
Severity: High
Advisory: GHSA-9qvw-46gf-4fv8
CVE: CVE-2021-45702
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9qvw-46gf-4fv8
Type: github-advisory

## Affected
- crates.io: `tremor-script` — affected >=0.7.2 <0.11.6

## Details
An issue was discovered in the tremor-script crate before 0.11.6 for Rust. A merge operation may result in a use-after-free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45702
- https://github.com/tremor-rs/tremor-runtime/pull/1217
- https://github.com/tremor-rs/tremor-runtime/commit/1a2efcdbe68e5e7fd0a05836ac32d2cde78a0b2e
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tremor-script/RUSTSEC-2021-0111.md
- https://rustsec.org/advisories/RUSTSEC-2021-0111.html
