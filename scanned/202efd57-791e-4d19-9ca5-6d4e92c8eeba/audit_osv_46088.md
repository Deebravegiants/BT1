# [M] JLSEC-2026-668

## Summary
Severity: Medium
Advisory: JLSEC-2026-668
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-668
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
wolfSSL through 5.0.0 allows an attacker to cause a denial of service and infinite loop in the client component by sending crafted traffic from a Machine-in-the-Middle (MITM) position. The root cause is that the client module accepts TLS messages that normally are only sent to TLS servers.

## References
- https://github.com/wolfSSL/wolfssl/releases
- https://www.wolfssl.com/docs/security-vulnerabilities/
