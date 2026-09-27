# [H] CVE-2018-16413

## Summary
Severity: High
Advisory: CVE-2018-16413
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16413
Type: osv

## Details
ImageMagick 7.0.8-11 Q16 has a heap-based buffer over-read in the MagickCore/quantum-private.h PushShortPixel function when called from the coders/psd.c ParseImageResourceBlocks function.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- https://usn.ubuntu.com/4034-1/
- http://www.securityfocus.com/bid/105241
- https://lists.debian.org/debian-lts-announce/2018/10/msg00002.html
- https://www.debian.org/security/2018/dsa-4316
- https://github.com/ImageMagick/ImageMagick/issues/1249
- https://github.com/ImageMagick/ImageMagick/issues/1251
