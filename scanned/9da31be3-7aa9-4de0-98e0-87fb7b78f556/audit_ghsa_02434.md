# [H] Use after free in generic-array

## Summary
Severity: High
Advisory: GHSA-3358-4f7f-p4j4
CVE: CVE-2020-36465
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3358-4f7f-p4j4
Type: github-advisory

## Affected
- crates.io: `generic-array` — affected >=0.13.0 <0.13.3
- crates.io: `generic-array` — affected >=0.12.0 <0.12.4
- crates.io: `generic-array` — affected >=0.11.0 <0.11.2
- crates.io: `generic-array` — affected >=0.10.0 <0.10.1
- crates.io: `generic-array` — affected >=0.8.0 <0.9.1

## Details
An issue was discovered in the generic-array crate before 0.13.3 for Rust. It violates soundness by using the arr! macro to extend lifetimes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36465
- https://github.com/fizyk20/generic-array/issues/98
- https://github.com/fizyk20/generic-array
- https://rustsec.org/advisories/RUSTSEC-2020-0146.html
