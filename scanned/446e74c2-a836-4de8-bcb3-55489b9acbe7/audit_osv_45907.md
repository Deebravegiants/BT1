# [M] Mbed TLS timing side channel in RSA and CBC/ECB decryption

## Summary
Severity: Medium
Advisory: JLSEC-2026-463
Ecosystem: Julia
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-463
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected unspecified

## Details
In Mbed TLS through 4.0.0, there is a compiler-induced timing side channel (in RSA and CBC/ECB decryption) that only occurs with LLVM's select-optimize feature. TF-PSA-Crypto through 1.0.0 is also affected.

## References
- https://github.com/Mbed-TLS/TF-PSA-Crypto/releases
- https://github.com/Mbed-TLS/mbedtls/releases
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-compiler-induced-constant-time-violations/
