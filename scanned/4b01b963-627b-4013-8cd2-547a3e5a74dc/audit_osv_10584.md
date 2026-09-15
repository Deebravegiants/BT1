# [M] CVE-2017-17504

## Summary
Severity: Medium
Advisory: CVE-2017-17504
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17504
Type: osv

## Details
ImageMagick before 7.0.7-12 has a coders/png.c Magick_png_read_raw_profile heap-based buffer over-read via a crafted file, related to ReadOneMNGImage.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00000.html
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4074
- https://www.debian.org/security/2018/dsa-4204
- https://github.com/ImageMagick/ImageMagick/issues/872
