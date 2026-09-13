# [H] ALPINE-CVE-2026-33636

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33636
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33636
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.6.36 <1.6.56-r0
- Alpine:v3.21: `libpng` — affected >=1.6.36 <1.6.56-r0
- Alpine:v3.22: `libpng` — affected >=1.6.36 <1.6.56-r0
- Alpine:v3.23: `libpng` — affected >=1.6.36 <1.6.56-r0
- Alpine:v3.24: `libpng` — affected >=1.6.36 <1.6.56-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. In versions 1.6.36 through 1.6.55, an out-of-bounds read and write exists in libpng's ARM/AArch64 Neon-optimized palette expansion path. When expanding 8-bit paletted rows to RGB or RGBA, the Neon loop processes a final partial chunk without verifying that enough input pixels remain. Because the implementation works backward from the end of the row, the final iteration dereferences pointers before the start of the row buffer (OOB read) and writes expanded pixel data to the same underflowed positions (OOB write). This is reachable via normal decoding of attacker-controlled PNG input if Neon is enabled. Version 1.6.56 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33636
