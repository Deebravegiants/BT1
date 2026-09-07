# [H] Out of bounds read in bumpalo

## Summary
Severity: High
Advisory: GHSA-vqx7-pw4r-29rr
CVE: CVE-2020-35861
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vqx7-pw4r-29rr
Type: github-advisory

## Affected
- crates.io: `bumpalo` — affected >=3.0.0 <3.2.1

## Details
An issue was discovered in the bumpalo crate before 3.2.1 for Rust. The realloc feature allows the reading of unknown memory. Attackers can potentially read cryptographic keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35861
- https://github.com/fitzgen/bumpalo/issues/69
- https://github.com/fitzgen/bumpalo
- https://rustsec.org/advisories/RUSTSEC-2020-0006.html
