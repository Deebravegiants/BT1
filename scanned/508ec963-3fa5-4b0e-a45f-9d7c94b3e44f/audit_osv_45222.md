# [M] Mbed TLS before 2.28.10 and 3.x before 3.6.3, on the client side, accepts servers that have trusted...

## Summary
Severity: Medium
Advisory: JLSEC-2025-227
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-227
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.10+0

## Details
Mbed TLS before 2.28.10 and 3.x before 3.6.3, on the client side, accepts servers that have trusted certificates for arbitrary hostnames unless the TLS client application calls `mbedtls_ssl_set_hostname`.

## References
- https://github.com/Mbed-TLS/mbedtls/issues/466
- https://github.com/Mbed-TLS/mbedtls/releases
- https://mastodon.social/@bagder/114219540623402700
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2025-03-1/
