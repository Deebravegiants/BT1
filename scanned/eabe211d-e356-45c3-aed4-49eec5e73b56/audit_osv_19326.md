# [M] CVE-2021-20224

## Summary
Severity: Medium
Advisory: CVE-2021-20224
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-20224
Type: osv

## Details
An integer overflow issue was discovered in ImageMagick's ExportIndexQuantum() function in MagickCore/quantum-export.c. Function calls to GetPixelIndex() could result in values outside the range of representable for the 'unsigned char'. When ImageMagick processes a crafted pdf file, this could lead to an undefined behaviour or a crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://github.com/ImageMagick/ImageMagick/commit/5af1dffa4b6ab984b5f13d1e91c95760d75f12a6
- https://github.com/ImageMagick/ImageMagick/pull/3083
- https://github.com/ImageMagick/ImageMagick6/commit/553054c1cb1e4e05ec86237afef76a32cd7c464d
