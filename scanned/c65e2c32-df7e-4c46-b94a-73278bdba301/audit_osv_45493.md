# [M] JLSEC-2026-1226

## Summary
Severity: Medium
Advisory: JLSEC-2026-1226
Ecosystem: Julia
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1226
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.2+0

## Details
In libexpat before 2.8.2, there is a heap-based buffer overflow in doProlog in xmlparse.c because scaffold backing array reallocation is mishandled when there is data-structure sharing across parsers.

## References
- https://github.com/libexpat/libexpat/pull/1272
