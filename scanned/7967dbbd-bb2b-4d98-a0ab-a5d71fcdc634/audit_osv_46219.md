# [H] JLSEC-2026-828

## Summary
Severity: High
Advisory: JLSEC-2026-828
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-828
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
ImageMagick before 7.0.8-50 has an integer overflow vulnerability in the function TIFFSeekCustomStream in `coders/tiff.c`.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://github.com/ImageMagick/ImageMagick/commit/fe5f4b85e6b1b54d3b4588a77133c06ade46d891
- https://github.com/ImageMagick/ImageMagick/commit/fe5f4b85e6b1b54d3b4588a77133c06ade46d891
- https://github.com/ImageMagick/ImageMagick/issues/1602
- https://github.com/ImageMagick/ImageMagick/issues/1602
- https://support.f5.com/csp/article/K03512441?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K03512441?utm_source=f5support&amp%3Butm_medium=RSS
