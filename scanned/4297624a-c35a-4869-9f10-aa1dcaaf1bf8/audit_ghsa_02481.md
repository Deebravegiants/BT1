# [C] Use after free in actix-utils

## Summary
Severity: Critical
Advisory: GHSA-hhw2-pqhf-vmx2
CVE: CVE-2020-35898
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hhw2-pqhf-vmx2
Type: github-advisory

## Affected
- crates.io: `actix-utils` — affected >=0 <2.0.0

## Details
An issue was discovered in the actix-utils crate before 2.0.0 for Rust. The Cell implementation allows obtaining more than one mutable reference to the same data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35898
- https://github.com/actix/actix-net/issues/160
- https://github.com/actix/actix-net/commit/0dca1a705ad1ff4885b3491ecb809a808e1de66c
- https://github.com/actix/actix-net
- https://rustsec.org/advisories/RUSTSEC-2020-0045.html
