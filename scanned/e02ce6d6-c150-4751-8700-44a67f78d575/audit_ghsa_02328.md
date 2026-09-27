# [H] Incorrect implementation in streebog

## Summary
Severity: High
Advisory: GHSA-39wr-f4ff-xm6p
CVE: CVE-2019-25007
CWE: CWE-617
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-39wr-f4ff-xm6p
Type: github-advisory

## Affected
- crates.io: `streebog` — affected >=0 <0.8.0

## Details
Internal update-sigma function was implemented incorrectly and depending on debug-assertions it could've caused an incorrect result or panic for certain inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25007
- https://github.com/RustCrypto/hashes/pull/91
- https://github.com/RustCrypto/hashes/tree/master/streebog
- https://rustsec.org/advisories/RUSTSEC-2019-0030.html
