# [C] Use after free and double free in bitvec

## Summary
Severity: Critical
Advisory: GHSA-7cjc-hvxf-gqh7
CVE: CVE-2020-35862
CWE: CWE-415, CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7cjc-hvxf-gqh7
Type: github-advisory

## Affected
- crates.io: `bitvec` — affected >=0.11.0 <0.17.4

## Details
An issue was discovered in the bitvec crate before 0.17.4 for Rust. BitVec to BitBox conversion leads to a use-after-free or double free.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35862
- https://github.com/myrrlyn/bitvec/issues/55
- https://github.com/myrrlyn/bitvec
- https://rustsec.org/advisories/RUSTSEC-2020-0007.html
