# [H] JLSEC-2026-670

## Summary
Severity: High
Advisory: JLSEC-2026-670
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-670
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In wolfSSL before 5.2.0, a TLS 1.3 server cannot properly enforce a requirement for mutual authentication. A client can simply omit the `certificate_verify` message from the handshake, and never present a certificate.

## References
- https://github.com/wolfSSL/wolfssl/pull/4831
