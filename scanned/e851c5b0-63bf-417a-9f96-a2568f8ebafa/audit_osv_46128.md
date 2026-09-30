# [M] JLSEC-2026-709

## Summary
Severity: Medium
Advisory: JLSEC-2026-709
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-709
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
wolfSSL 5.8.4 on RISC-V RV32I architectures lacks a constant-time software implementation for 64-bit multiplication. The compiler-inserted `__muldi3` subroutine executes in variable time based on operand values. This affects multiple SP math functions (`sp_256_mul_9`, `sp_256_sqr_9`, etc.), leading to a timing side-channel that may expose sensitive cryptographic data.

## References
- https://github.com/wolfSSL/wolfssl/pull/9855
