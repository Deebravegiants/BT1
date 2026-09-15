# [M] rustls network-reachable panic in `Acceptor::accept`

## Summary
Severity: Medium
Advisory: GHSA-qg5g-gv98-5ffh
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-qg5g-gv98-5ffh
Type: github-advisory

## Affected
- crates.io: `rustls` — affected >=0.23.13 <0.23.18

## Details
A bug introduced in rustls 0.23.13 leads to a panic if the received TLS ClientHello is fragmented.  Only servers that use `rustls::server::Acceptor::accept()` are affected.

Servers that use `tokio-rustls`'s `LazyConfigAcceptor` API are affected.

Servers that use `tokio-rustls`'s `TlsAcceptor` API are not affected.

Servers that use `rustls-ffi`'s `rustls_acceptor_accept` API are affected.

## References
- https://github.com/rustls/rustls/issues/2227
- https://github.com/rustls/rustls
- https://rustsec.org/advisories/RUSTSEC-2024-0399.html
