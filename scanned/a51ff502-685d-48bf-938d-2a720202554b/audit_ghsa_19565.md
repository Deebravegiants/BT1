# [M] rust-openssl Use-After-Free in `Md::fetch` and `Cipher::fetch`

## Summary
Severity: Medium
Advisory: GHSA-4fcv-w3qc-ppgg
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-4fcv-w3qc-ppgg
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.39 <0.10.72

## Details
When a `Some(...)` value was passed to the `properties` argument of either of these functions, a use-after-free would result.

In practice this would nearly always result in OpenSSL treating the properties as an empty string (due to `CString::drop`'s behavior).

The maintainers thank [quitbug](https://github.com/quitbug/) for reporting this vulnerability to us.

## References
- https://github.com/sfackler/rust-openssl/pull/2390
- https://github.com/sfackler/rust-openssl/commit/87085bd67896b7f92e6de35d081f607a334beae4
- https://github.com/sfackler/rust-openssl
- https://rustsec.org/advisories/RUSTSEC-2025-0022.html
