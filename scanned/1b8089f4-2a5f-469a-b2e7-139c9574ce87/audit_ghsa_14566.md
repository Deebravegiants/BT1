# [M] `openssl` `X509NameBuilder::build` returned object is not thread safe

## Summary
Severity: Medium
Advisory: GHSA-3gxf-9r58-2ghg
Ecosystem: crates.io
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-3gxf-9r58-2ghg
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.9.7 <0.10.48

## Details
OpenSSL has a `modified` bit that it can set on on `X509_NAME` objects. If this bit is set then the object is not thread-safe even when it appears the code is not modifying the value.

Thanks to David Benjamin (Google) for reporting this issue.

## References
- https://github.com/sfackler/rust-openssl/pull/1854
- https://rustsec.org/advisories/RUSTSEC-2023-0022.html
