# [H] JLSEC-2026-832

## Summary
Severity: High
Advisory: JLSEC-2026-832
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-832
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
ImageMagick before 7.0.8-55 has a use-after-free in DestroyStringInfo in `MagickCore/string.c` because the error manager is mishandled in `coders/jpeg.c`.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15827
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15827
- https://github.com/ImageMagick/ImageMagick/commit/39f226a9c137f547e12afde972eeba7551124493
- https://github.com/ImageMagick/ImageMagick/commit/39f226a9c137f547e12afde972eeba7551124493
- https://github.com/ImageMagick/ImageMagick/compare/7.0.8-54...7.0.8-55
- https://github.com/ImageMagick/ImageMagick/compare/7.0.8-54...7.0.8-55
- https://github.com/ImageMagick/ImageMagick/issues/1641
- https://github.com/ImageMagick/ImageMagick/issues/1641
