# [M] bottlerocket dependency openssl has a double free vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3wxx-jxwc-mg39
Ecosystem: crates.io
Published: 2023-02-09
Source: https://osv.dev/vulnerability/GHSA-3wxx-jxwc-mg39
Type: osv

## Affected
- crates.io: `bottlerocket/update-operator` — affected >=0 <1.1.0

## Details
A double-free vulnerability exists in OpenSSL where it is possible to construct a malicious PEM file that has 0 bytes of payload data. This then points to data that has already been freed in memory which, when freed again, leads to a crash. Agents or clients compiled with OpenSSL may crash unexpectedly when parsing these PEM files. OpenSSL has been removed in bottlerocket/update-operator version 1.1.0 in favor of Rust-based TLS using rustls.

## References
- https://github.com/bottlerocket-os/bottlerocket-update-operator/security/advisories/GHSA-3wxx-jxwc-mg39
- https://github.com/bottlerocket-os/bottlerocket-update-operator
- https://github.com/bottlerocket-os/bottlerocket-update-operator/releases/tag/v1.1.0
- https://rustsec.org/advisories/RUSTSEC-2023-0010.html
- https://www.openssl.org/news/secadv/20230207.txt
