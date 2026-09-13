# [M] JLSEC-2026-198

## Summary
Severity: Medium
Advisory: JLSEC-2026-198
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-198
Type: osv

## Affected
- Julia: `NASM_jll` — affected >=0 <2.16.1+0

## Details
nasm version 2.14.01rc5, 2.15 contains a Buffer Overflow vulnerability in `asm/stdscan.c:130` that can result in Stack-overflow caused by triggering endless macro generation, crash the program. This attack appear to be exploitable via a crafted nasm input file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392514
