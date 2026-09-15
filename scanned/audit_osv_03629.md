# [M] ALPINE-CVE-2026-34757

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34757
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34757
Type: osv

## Affected
- Alpine:v3.20: `libpng` — affected >=1.0.9 <1.6.57-r0
- Alpine:v3.21: `libpng` — affected >=1.0.9 <1.6.57-r0
- Alpine:v3.22: `libpng` — affected >=1.0.9 <1.6.57-r0
- Alpine:v3.23: `libpng` — affected >=1.0.9 <1.6.57-r0
- Alpine:v3.24: `libpng` — affected >=1.0.9 <1.6.57-r0

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. From 1.0.9 to before 1.6.57, passing a pointer obtained from png_get_PLTE, png_get_tRNS, or png_get_hIST back into the corresponding setter on the same png_struct/png_info pair causes the setter to read from freed memory and copy its contents into the replacement buffer. The setter frees the internal buffer before copying from the caller-supplied pointer, which now dangles. The freed region may contain stale data (producing silently corrupted chunk metadata) or data from subsequent heap allocations (leaking unrelated heap contents into the chunk struct). This vulnerability is fixed in 1.6.57.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34757
