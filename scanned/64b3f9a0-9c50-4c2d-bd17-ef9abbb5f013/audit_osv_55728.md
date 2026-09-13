# [M] bottlerocket dependency openssl provides streaming of ASN.1 data via a BIO

## Summary
Severity: Medium
Advisory: GHSA-j79x-vvgm-w73w
Ecosystem: crates.io
Published: 2023-02-09
Source: https://osv.dev/vulnerability/GHSA-j79x-vvgm-w73w
Type: osv

## Affected
- crates.io: `bottlerocket/update-operator` — affected >=0 <1.1.0

## Details
An OpenSSL public API provides streaming of ASN.1 data via a BIO. It is possible for a malicious third party to use the BIO to access unfreed memory pointers that are not cleaned up after execution of the API. Freeing these memory pointers will result in a crash. Agents and clients compiled with OpenSSL may see unexpected crashes. OpenSSL has been removed in bottlerocket/update-operator version 1.1.0 in favor of Rust-based TLS using rustls.

## References
- https://github.com/bottlerocket-os/bottlerocket-update-operator/security/advisories/GHSA-j79x-vvgm-w73w
- https://github.com/bottlerocket-os/bottlerocket-update-operator
- https://github.com/bottlerocket-os/bottlerocket-update-operator/releases/tag/v1.1.0
- https://rustsec.org/advisories/RUSTSEC-2023-0009.html
- https://www.openssl.org/news/secadv/20230207.txt
