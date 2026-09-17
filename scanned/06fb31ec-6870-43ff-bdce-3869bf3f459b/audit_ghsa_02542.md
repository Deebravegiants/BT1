# [C] Access of Uninitialized Pointer in linked-hash-map

## Summary
Severity: Critical
Advisory: GHSA-r43h-gmrm-h5c9
CVE: CVE-2020-25573
CWE: CWE-824
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r43h-gmrm-h5c9
Type: github-advisory

## Affected
- crates.io: `linked-hash-map` — affected >=0 <0.5.3

## Details
An issue was discovered in the linked-hash-map crate before 0.5.3 for Rust. It creates an uninitialized NonNull pointer, which violates a non-null constraint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25573
- https://github.com/contain-rs/linked-hash-map/pull/100
- https://github.com/contain-rs/linked-hash-map
- https://rustsec.org/advisories/RUSTSEC-2020-0026.html
