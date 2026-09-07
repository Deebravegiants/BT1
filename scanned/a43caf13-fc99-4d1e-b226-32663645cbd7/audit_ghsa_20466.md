# [C] Use of a Broken or Risky Cryptographic Algorithm in crypto2

## Summary
Severity: Critical
Advisory: GHSA-9hfg-pxr6-q4vp
CVE: CVE-2021-45709
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9hfg-pxr6-q4vp
Type: github-advisory

## Affected
- crates.io: `crypto2` — affected >=0

## Details
The implementation does not enforce alignment requirements on input slices while incorrectly assuming 4-byte alignment through an unsafe call to std::slice::from_raw_parts_mut, which breaks the contract and introduces undefined behavior.

This affects Chacha20 encryption and decryption in crypto2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45709
- https://github.com/shadowsocks/crypto2/issues/27
- https://github.com/shadowsocks/crypto2
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/crypto2/RUSTSEC-2021-0121.md
- https://rustsec.org/advisories/RUSTSEC-2021-0121.html
