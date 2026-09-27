# [H] bottlerocket dependency openssl is vulnerable to dereferenced null pointers

## Summary
Severity: High
Advisory: GHSA-qf87-q4gg-cg43
Ecosystem: crates.io
Published: 2023-02-09
Source: https://osv.dev/vulnerability/GHSA-qf87-q4gg-cg43
Type: osv

## Affected
- crates.io: `bottlerocket/update-operator` — affected >=0 <1.1.0

## Details
A null pointer in OpenSSL can be dereferenced when signatures are being verified in malformed PKCS7 data. Agents or clients compiled with OpenSSL may experience unexpected crashes. OpenSSL has been removed in bottlerocket/update-operator version 1.1.0 in favor of Rust-based TLS using rustls.

## References
- https://github.com/bottlerocket-os/bottlerocket-update-operator/security/advisories/GHSA-qf87-q4gg-cg43
- https://github.com/bottlerocket-os/bottlerocket-update-operator
- https://github.com/bottlerocket-os/bottlerocket-update-operator/releases/tag/v1.1.0
- https://www.openssl.org/news/secadv/20230207.txt
