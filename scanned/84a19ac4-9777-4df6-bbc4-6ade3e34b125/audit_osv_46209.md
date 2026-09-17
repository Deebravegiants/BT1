# [H] JLSEC-2026-816

## Summary
Severity: High
Advisory: JLSEC-2026-816
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-816
Type: osv

## Affected
- Julia: `Giflib_jll` — affected >=0 <5.2.1+0

## Details
A memory leak (out-of-memory) in gif2rgb in `util/gif2rgb.c` in giflib 5.1.4 allows remote attackers trigger an out of memory exception or denial of service via a gif format file.

## References
- https://sourceforge.net/p/giflib/bugs/157/
- https://sourceforge.net/p/giflib/bugs/157/
