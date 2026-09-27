# [C] Out-of-bounds Write in actix-web

## Summary
Severity: Critical
Advisory: GHSA-9qj6-4rfq-vm84
CVE: CVE-2018-25024
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9qj6-4rfq-vm84
Type: github-advisory

## Affected
- crates.io: `actix-web` — affected >=0 <0.7.19

## Details
An issue was discovered in the actix-web crate before 0.7.19 for Rust. It can unsoundly coerce an immutable reference into a mutable reference, leading to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25024
- https://github.com/actix/actix-web/issues/289
- https://github.com/actix/actix-web.git
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/actix-web/RUSTSEC-2018-0019.md
- https://rustsec.org/advisories/RUSTSEC-2018-0019.html
