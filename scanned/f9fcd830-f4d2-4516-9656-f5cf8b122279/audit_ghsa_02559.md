# [M] Use after free in actix-service

## Summary
Severity: Medium
Advisory: GHSA-whc7-5p35-4ww2
CVE: CVE-2020-35899
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-whc7-5p35-4ww2
Type: github-advisory

## Affected
- crates.io: `actix-service` — affected >=0 <1.0.6

## Details
An issue was discovered in the actix-service crate before 1.0.6 for Rust. The Cell implementation allows obtaining more than one mutable reference to the same data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35899
- https://github.com/actix/actix-net/pull/158
- https://github.com/actix/actix-net/commit/a67e38b4a07c92a3c81fa833f9eb1e91e74e39b7
- https://github.com/actix/actix-net
- https://rustsec.org/advisories/RUSTSEC-2020-0046.html
