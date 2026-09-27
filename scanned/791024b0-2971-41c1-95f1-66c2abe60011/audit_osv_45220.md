# [H] An issue was discovered in Mbed TLS 2.18.0 through 2.28.x before 2.28.8 and 3.x before 3.6.0, and...

## Summary
Severity: High
Advisory: JLSEC-2025-225
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-225
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.10+0

## Details
An issue was discovered in Mbed TLS 2.18.0 through 2.28.x before 2.28.8 and 3.x before 3.6.0, and Mbed Crypto. The PSA Crypto API mishandles shared memory.

## References
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2024-03.md
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5YE3QRREGJC6K34JD4LZ5P3IALNX4QYY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6UZNBMKYEV2J5DI7R4BQGL472V7X3WJY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NCDU52ZDA7TX3HC5JCU6ZZIJQOPTNBK6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5YE3QRREGJC6K34JD4LZ5P3IALNX4QYY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6UZNBMKYEV2J5DI7R4BQGL472V7X3WJY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NCDU52ZDA7TX3HC5JCU6ZZIJQOPTNBK6/
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
