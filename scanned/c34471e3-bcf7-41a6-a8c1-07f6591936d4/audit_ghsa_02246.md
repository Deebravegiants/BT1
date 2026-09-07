# [C] Overflow in libsecp256k1

## Summary
Severity: Critical
Advisory: GHSA-g4vj-x7v9-h82m
CVE: CVE-2021-38195
CWE: CWE-190, CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g4vj-x7v9-h82m
Type: github-advisory

## Affected
- crates.io: `libsecp256k1` — affected >=0 <0.5.0

## Details
An issue was discovered in the libsecp256k1 crate before 0.5.0 for Rust. It can verify an invalid signature because it allows the R or S parameter to be larger than the curve order, aka an overflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38195
- https://github.com/paritytech/libsecp256k1/pull/67
- https://github.com/paritytech/libsecp256k1
- https://rustsec.org/advisories/RUSTSEC-2021-0076.html
