# [H] CVE-2019-13391

## Summary
Severity: High
Advisory: CVE-2019-13391
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-07
Source: https://osv.dev/vulnerability/CVE-2019-13391
Type: osv

## Details
In ImageMagick 7.0.8-50 Q16, ComplexImages in MagickCore/fourier.c has a heap-based buffer over-read because of incorrect calls to GetCacheViewVirtualPixels.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://usn.ubuntu.com/4192-1/
- https://github.com/ImageMagick/ImageMagick/commit/7c2c5ba5b8e3a0b2b82f56c71dfab74ed4006df7
- https://github.com/ImageMagick/ImageMagick/issues/1588
- https://github.com/ImageMagick/ImageMagick6/commit/f6ffc702c6eecd963587273a429dcd608c648984
