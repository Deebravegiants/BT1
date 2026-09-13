# [H] CVE-2019-15541

## Summary
Severity: High
Advisory: CVE-2019-15541
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-26
Source: https://osv.dev/vulnerability/CVE-2019-15541
Type: osv

## Details
rustls-mio/examples/tlsserver.rs in the rustls crate before 0.16.0 for Rust allows attackers to cause a denial of service (loop of conn_event and ready) by arranging for a client to never be writable.

## References
- https://github.com/ctz/rustls/compare/cd66549...17ee52c
- https://github.com/ctz/rustls/issues/285
- https://github.com/ctz/rustls/commit/a93ee1abd2ab19ebe4bf9d684d56637ee54a6074
