# [M] Buffer Overflow vulnerability in libpng 1.6.43-1.6.46 allows a local attacker to cause a denial of...

## Summary
Severity: Medium
Advisory: JLSEC-2026-10
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/JLSEC-2026-10
Type: osv

## Affected
- Julia: `libpng_jll` — affected >=1.6.43+0 <1.6.47+0

## Details
Buffer Overflow vulnerability in libpng 1.6.43-1.6.46 allows a local attacker to cause a denial of service via `png_create_read_struct()` function.

## References
- https://gist.github.com/kittener/506516f8c22178005b4379c8b2a7de20
- https://github.com/pnggroup/libpng/issues/655
