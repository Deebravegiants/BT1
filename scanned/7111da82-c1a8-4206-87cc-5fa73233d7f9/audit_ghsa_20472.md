# [C] Deserialization of Untrusted Data in rust-cpuid

## Summary
Severity: Critical
Advisory: GHSA-w428-f65r-h4q2
CVE: CVE-2021-45687
CWE: CWE-502
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-w428-f65r-h4q2
Type: github-advisory

## Affected
- crates.io: `raw-cpuid` — affected >=3.1.0 <9.1.1

## Details
An issue was discovered in the raw-cpuid crate before 9.1.1 for Rust. If the serialize feature is used (which is not the the default), a Deserialize operation may lack sufficient validation, leading to memory corruption or a panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45687
- https://github.com/gz/rust-cpuid/issues/43
- https://github.com/gz/rust-cpuid
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/raw-cpuid/RUSTSEC-2021-0089.md
- https://rustsec.org/advisories/RUSTSEC-2021-0089.html
