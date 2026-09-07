# [M] `openssl` `X509VerifyParamRef::set_host` buffer over-read

## Summary
Severity: Medium
Advisory: GHSA-xcf7-rvmh-g6q4
CVE: CVE-2023-53159
CWE: CWE-126
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-xcf7-rvmh-g6q4
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.0 <0.10.55

## Details
When this function was passed an empty string, `openssl` would attempt to call `strlen` on it, reading arbitrary memory until it reached a NUL byte.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53159
- https://github.com/sfackler/rust-openssl/issues/1965
- https://github.com/sfackler/rust-openssl/pull/1968
- https://github.com/sfackler/rust-openssl
- https://rustsec.org/advisories/RUSTSEC-2023-0044.html
