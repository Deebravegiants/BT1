# [M] JLSEC-2026-202

## Summary
Severity: Medium
Advisory: JLSEC-2026-202
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-202
Type: osv

## Affected
- Julia: `NASM_jll` — affected >=0 <2.16.1+0

## Details
Buffer overflow vulnerability in `quote_for_pmake` in `asm/nasm.c` in nasm before 2.15.05 allows attackers to cause a denial of service via crafted file.

## References
- https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html
- https://gist.github.com/naihsin/b96e2c5c2c81621b46557fd7aacd165f
- https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/
