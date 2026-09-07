# [C] Double free in through

## Summary
Severity: Critical
Advisory: GHSA-5hpj-m323-cphm
CVE: CVE-2021-29940
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5hpj-m323-cphm
Type: github-advisory

## Affected
- crates.io: `through` — affected >=0

## Details
An issue was discovered in the through crate through 2021-02-18 for Rust. There is a double free (in through and through_and) upon a panic of the map function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29940
- https://github.com/gretchenfrage/through/issues/1
- https://github.com/gretchenfrage/through
- https://rustsec.org/advisories/RUSTSEC-2021-0049.html
