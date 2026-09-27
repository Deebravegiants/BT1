# [M] JLSEC-2026-1107

## Summary
Severity: Medium
Advisory: JLSEC-2026-1107
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1107
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
In LibRaw, there is an out-of-bounds read vulnerability within the "LibRaw::parseSonySRF()" function (`libraw\src\metadata\sony.cpp`) when processing srf files.

## References
- https://github.com/LibRaw/LibRaw/commit/c243f4539233053466c1309bde606815351bee81
- https://github.com/LibRaw/LibRaw/commit/c243f4539233053466c1309bde606815351bee81
- https://github.com/LibRaw/LibRaw/issues/283
- https://github.com/LibRaw/LibRaw/issues/283
