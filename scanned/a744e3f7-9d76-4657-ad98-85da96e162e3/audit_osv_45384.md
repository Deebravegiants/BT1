# [M] JLSEC-2026-1106

## Summary
Severity: Medium
Advisory: JLSEC-2026-1106
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1106
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, there is a memory corruption vulnerability within the "crxFreeSubbandData()" function (`libraw\src\decoders\crx.cpp`) when processing cr3 files.

## References
- https://github.com/LibRaw/LibRaw/commit/e41f331e90b383e3208cefb74e006df44bf3a4b8
- https://github.com/LibRaw/LibRaw/commit/e41f331e90b383e3208cefb74e006df44bf3a4b8
- https://github.com/LibRaw/LibRaw/issues/279
- https://github.com/LibRaw/LibRaw/issues/279
