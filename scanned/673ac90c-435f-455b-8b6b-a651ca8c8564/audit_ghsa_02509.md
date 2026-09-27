# [H] Insufficient size checks in ws

## Summary
Severity: High
Advisory: GHSA-rh7x-ppxx-p34c
CVE: CVE-2020-35896
CWE: CWE-400, CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rh7x-ppxx-p34c
Type: github-advisory

## Affected
- crates.io: `ws` — affected >=0

## Details
An issue was discovered in the ws crate through 2020-09-25 for Rust. The outgoing buffer is not properly limited, leading to a remote memory-consumption attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35896
- https://github.com/housleyjk/ws-rs/issues/291
- https://github.com/housleyjk/ws-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0043.html
