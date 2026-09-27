# [C] Mbed TLS serialized session data is not cryptographically protected

## Summary
Severity: Critical
Advisory: JLSEC-2026-467
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-467
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected unspecified

## Details
An issue was discovered in Mbed TLS versions from 2.19.0 up to 3.6.5, Mbed TLS 4.0.0. Insufficient protection of serialized SSL context or session structures allows an attacker who can modify the serialized structures to induce memory corruption, leading to arbitrary code execution. This is caused by Incorrect Use of Privileged APIs.

## References
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-serialized-data/
