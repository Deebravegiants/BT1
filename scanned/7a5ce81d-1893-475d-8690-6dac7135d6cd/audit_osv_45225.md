# [H] Mbed TLS before 3.6.4 has a NULL pointer dereference because `mbedtls_asn1_store_named_data` can...

## Summary
Severity: High
Advisory: JLSEC-2025-230
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-230
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.1010+0

## Details
Mbed TLS before 3.6.4 has a NULL pointer dereference because `mbedtls_asn1_store_named_data` can trigger conflicting data with val.p of NULL but val.len greater than zero.

## References
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-6.md
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
