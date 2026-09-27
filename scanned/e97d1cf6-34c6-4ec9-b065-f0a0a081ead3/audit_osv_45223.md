# [H] Mbed TLS before 3.6.4 has a race condition in AESNI detection if certain compiler optimizations...

## Summary
Severity: High
Advisory: JLSEC-2025-228
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-228
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.1010+0

## Details
Mbed TLS before 3.6.4 has a race condition in AESNI detection if certain compiler optimizations occur. An attacker may be able to extract an AES key from a multithreaded program, or perform a GCM forgery.

## References
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-1.md
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
