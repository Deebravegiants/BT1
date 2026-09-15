# [M] JLSEC-2026-201

## Summary
Severity: Medium
Advisory: JLSEC-2026-201
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-201
Type: osv

## Affected
- Julia: `NASM_jll` — affected >=0 <2.16.1+0

## Details
A stack-use-after-scope issue discovered in `expand_mmac_params` function in preproc.c in nasm before 2.15.04 allows remote attackers to cause a denial of service via crafted asm file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392643
