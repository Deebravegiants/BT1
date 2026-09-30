# [C] Use after free in libflate

## Summary
Severity: Critical
Advisory: GHSA-rpcm-whqc-jfw8
CVE: CVE-2019-15552
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rpcm-whqc-jfw8
Type: github-advisory

## Affected
- crates.io: `libflate` — affected >=0.1.14 <0.1.25

## Details
An issue was discovered in the libflate crate before 0.1.25 for Rust. MultiDecoder::read has a use-after-free, leading to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15552
- https://github.com/sile/libflate/issues/35
- https://github.com/sile/libflate/pull/37
- https://github.com/sile/libflate/commit/ffeff7c65deac5a6f886db2a59bcae4e420e4706
- https://github.com/sile/libflate
- https://rustsec.org/advisories/RUSTSEC-2019-0010.html
