# [M] An issue was discovered in Mbed TLS before 2.28.9 and 3.x before 3.6.1, in which the user-selected...

## Summary
Severity: Medium
Advisory: JLSEC-2025-226
Ecosystem: Julia
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-226
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=2.26.0+0 <2.28.10+0

## Details
An issue was discovered in Mbed TLS before 2.28.9 and 3.x before 3.6.1, in which the user-selected algorithm is not used. Unlike previously documented, enabling `MBEDTLS_PSA_HMAC_DRBG_MD_TYPE` does not cause the PSA subsystem to use `HMAC_DRBG`: it uses `HMAC_DRBG` only when `MBEDTLS_PSA_CRYPTO_EXTERNAL_RNG` and `MBEDTLS_CTR_DRBG_C` are disabled.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2024-08-1/
