# [M] JLSEC-2026-826

## Summary
Severity: Medium
Advisory: JLSEC-2026-826
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-826
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
LocaleLowercase in `MagickCore/locale.c` in ImageMagick before 7.0.8-32 allows out-of-bounds access, leading to a SIGSEGV.

## References
- https://github.com/ImageMagick/ImageMagick/commit/07eebcd72f45c8fd7563d3f9ec5d2bed48f65f36
- https://github.com/ImageMagick/ImageMagick/commit/07eebcd72f45c8fd7563d3f9ec5d2bed48f65f36
- https://github.com/ImageMagick/ImageMagick/commit/58d9c46929ca0828edde34d263700c3a5fe8dc3c
- https://github.com/ImageMagick/ImageMagick/commit/58d9c46929ca0828edde34d263700c3a5fe8dc3c
- https://github.com/ImageMagick/ImageMagick/commit/edc7d3035883ddca8413e4fe7689aa2e579ef04a
- https://github.com/ImageMagick/ImageMagick/commit/edc7d3035883ddca8413e4fe7689aa2e579ef04a
- https://github.com/ImageMagick/ImageMagick/issues/1495
- https://github.com/ImageMagick/ImageMagick/issues/1495
