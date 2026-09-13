# [M] Use of a Broken or Risky Cryptographic Algorithm in the function `mbedtls_mpi_exp_mod()` in lignum.c...

## Summary
Severity: Medium
Advisory: JLSEC-2025-221
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-221
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.27.0+0

## Details
Use of a Broken or Risky Cryptographic Algorithm in the function `mbedtls_mpi_exp_mod()` in lignum.c in Mbed TLS Mbed TLS all versions before 3.0.0, 2.27.0 or 2.16.11 allows attackers with access to precise enough timing and memory access information (typically an untrusted operating system attacking a secure enclave such as SGX or the TrustZone secure world) to recover the private keys used in RSA.

## References
- https://github.com/ARMmbed/mbedtls/releases/
- https://kouzili.com/Load-Step.pdf
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2021-07-1
