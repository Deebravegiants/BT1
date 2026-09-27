# [M] JLSEC-2026-710

## Summary
Severity: Medium
Advisory: JLSEC-2026-710
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-710
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
In wolfSSL 5.8.4, constant-time masking logic in `sp_256_get_entry_256_9` is optimized into conditional branches (bnez) by GCC when targeting RISC-V RV32I with -O3. This transformation breaks the side-channel resistance of ECC scalar multiplication, potentially allowing a local attacker to recover secret keys via timing analysis.

## References
- https://github.com/wolfSSL/wolfssl/pull/9855
