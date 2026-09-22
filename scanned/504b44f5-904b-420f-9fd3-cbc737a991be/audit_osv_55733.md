# [M] bottlerocket dependency openssl is vulnerable to read buffer overflow via X.509 verification

## Summary
Severity: Medium
Advisory: GHSA-pj34-fpw3-83qj
Ecosystem: crates.io
Published: 2023-02-09
Source: https://osv.dev/vulnerability/GHSA-pj34-fpw3-83qj
Type: osv

## Affected
- crates.io: `bottlerocket/update-operator` — affected >=0 <1.1.0

## Details
A read buffer overflow can be triggered in OpenSSL X.509 verification during name constraint checking. Note that this occurs after the certificate chain has been verified and would require a compromised CA. This can cause a client or agent compiled with OpenSSL to crash unexpectedly. OpenSSL has been removed in bottlerocket/update-operator version 1.1.0 in favor of Rust-based TLS using rustls.

## References
- https://github.com/bottlerocket-os/bottlerocket-update-operator/security/advisories/GHSA-pj34-fpw3-83qj
- https://github.com/bottlerocket-os/bottlerocket-update-operator
- https://github.com/bottlerocket-os/bottlerocket-update-operator/releases/tag/v1.1.0
- https://www.openssl.org/news/secadv/20230207.txt
