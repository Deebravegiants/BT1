# [M] JLSEC-2026-669

## Summary
Severity: Medium
Advisory: JLSEC-2026-669
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-669
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In wolfSSL before 5.2.0, certificate validation may be bypassed during attempted authentication by a TLS 1.3 client to a TLS 1.3 server. This occurs when the `sig_algo` field differs between the `certificate_verify` message and the certificate message.

## References
- https://github.com/wolfSSL/wolfssl/pull/4813
- https://www.wolfssl.com/docs/security-vulnerabilities/
