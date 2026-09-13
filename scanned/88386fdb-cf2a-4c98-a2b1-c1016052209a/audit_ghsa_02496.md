# [C] Algorithms compute incorrect results in blake2

## Summary
Severity: Critical
Advisory: GHSA-4x25-pvhw-5224
CVE: CVE-2019-16143
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4x25-pvhw-5224
Type: github-advisory

## Affected
- crates.io: `blake2` — affected >=0 <0.8.1

## Details
An issue was discovered in the blake2 crate before 0.8.1 for Rust. The BLAKE2b and BLAKE2s algorithms, when used with HMAC, produce incorrect results because the block sizes are half of the required sizes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16143
- https://github.com/RustCrypto/MACs/issues/19
- https://github.com/RustCrypto/hashes/tree/master/blake2
- https://rustsec.org/advisories/RUSTSEC-2019-0019.html
