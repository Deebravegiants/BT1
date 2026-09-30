# [H] Use of uninitialized buffer in rkyv

## Summary
Severity: High
Advisory: GHSA-w5cr-frph-hw7f
CVE: CVE-2021-31919
CWE: CWE-772, CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w5cr-frph-hw7f
Type: github-advisory

## Affected
- crates.io: `rkyv` — affected >=0 <0.6.0

## Details
An issue was discovered in the rkyv crate before 0.6.0 for Rust. When an archive is created via serialization, the archive content may contain uninitialized values of certain parts of a struct.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31919
- https://github.com/djkoloski/rkyv/issues/113
- https://github.com/djkoloski/rkyv/commit/9c65ae9c2c67dd949b5c3aba9b8eba6da802ab7e
- https://github.com/djkoloski/rkyv/commit/f141b560523a20557db6540576d153010bd18712
- https://rustsec.org/advisories/RUSTSEC-2021-0054.html
