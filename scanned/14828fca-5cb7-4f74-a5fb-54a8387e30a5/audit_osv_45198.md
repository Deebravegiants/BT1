# [M] Mbed TLS before 2.28.10 and 3.x before 3.6.3, in some cases of failed memory allocation or hardware...

## Summary
Severity: Medium
Advisory: JLSEC-2025-187
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-23
Source: https://osv.dev/vulnerability/JLSEC-2025-187
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.28.10+0

## Details
Mbed TLS before 2.28.10 and 3.x before 3.6.3, in some cases of failed memory allocation or hardware errors, uses uninitialized stack memory to compose the TLS Finished message, potentially leading to authentication bypasses such as replays.

## References
- https://github.com/Mbed-TLS/mbedtls/releases
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2025-03-2/
