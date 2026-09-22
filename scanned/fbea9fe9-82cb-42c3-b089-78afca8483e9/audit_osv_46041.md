# [M] JLSEC-2026-599

## Summary
Severity: Medium
Advisory: JLSEC-2026-599
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-599
Type: osv

## Affected
- Julia: `YASM_jll` — affected unspecified

## Details
A memory leak issue discovered in YASM v.1.3.0 allows a local attacker to cause a denial of service via the `new_Token` function in the modules/preprocs/nasm/nasm-pp:1512.

## References
- https://github.com/hanxuer/crashes/blob/main/yasm/04/readme.md
