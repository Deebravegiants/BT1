# [H] Double free in endian_trait

## Summary
Severity: High
Advisory: GHSA-vpw8-43wm-rxw5
CVE: CVE-2021-29929
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vpw8-43wm-rxw5
Type: github-advisory

## Affected
- crates.io: `endian_trait` — affected >=0

## Details
An issue was discovered in the endian_trait crate through 2021-01-04 for Rust. A double drop can occur when a user-provided Endian impl panics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29929
- https://gitlab.com/myrrlyn/endian_trait
- https://gitlab.com/myrrlyn/endian_trait/-/issues/1
- https://rustsec.org/advisories/RUSTSEC-2021-0039.html
