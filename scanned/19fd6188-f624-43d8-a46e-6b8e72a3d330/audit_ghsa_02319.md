# [M] Data races in atom

## Summary
Severity: Medium
Advisory: GHSA-9cg2-2j2h-59v9
CVE: CVE-2020-35897
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9cg2-2j2h-59v9
Type: github-advisory

## Affected
- crates.io: `atom` — affected >=0 <0.3.6

## Details
The atom crate contains a security issue revolving around its implementation of the Send trait. It incorrectly allows any arbitrary type to be sent across threads potentially leading to use-after-free issues through memory races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35897
- https://github.com/slide-rs/atom/issues/13
- https://github.com/slide-rs/atom
- https://rustsec.org/advisories/RUSTSEC-2020-0044.html
