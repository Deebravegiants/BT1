# [M] JLSEC-2026-878

## Summary
Severity: Medium
Advisory: JLSEC-2026-878
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-878
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
An integer overflow issue was discovered in ImageMagick's ExportIndexQuantum() function in `MagickCore/quantum-export.c`. Function calls to GetPixelIndex() could result in values outside the range of representable for the 'unsigned char'. When ImageMagick processes a crafted pdf file, this could lead to an undefined behaviour or a crash.

## References
- https://github.com/ImageMagick/ImageMagick/commit/5af1dffa4b6ab984b5f13d1e91c95760d75f12a6
- https://github.com/ImageMagick/ImageMagick/commit/5af1dffa4b6ab984b5f13d1e91c95760d75f12a6
- https://github.com/ImageMagick/ImageMagick/pull/3083
- https://github.com/ImageMagick/ImageMagick/pull/3083
- https://github.com/ImageMagick/ImageMagick6/commit/553054c1cb1e4e05ec86237afef76a32cd7c464d
- https://github.com/ImageMagick/ImageMagick6/commit/553054c1cb1e4e05ec86237afef76a32cd7c464d
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
