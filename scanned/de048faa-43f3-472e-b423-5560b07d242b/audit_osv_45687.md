# [M] JLSEC-2026-204

## Summary
Severity: Medium
Advisory: JLSEC-2026-204
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-204
Type: osv

## Affected
- Julia: `NASM_jll` — affected >=2.16.1+0 <2.16.3+0

## Details
NASM v2.16 was discovered to contain a global buffer overflow in the component `dbgdbg_typevalue` at `/output/outdbg.c`.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392814
