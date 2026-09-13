# [M] CVE-2017-11639

## Summary
Severity: Medium
Advisory: CVE-2017-11639
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11639
Type: osv

## Details
When ImageMagick 7.0.6-1 processes a crafted file in convert, it can lead to a heap-based buffer over-read in the WriteCIPImage() function in coders/cip.c, related to the GetPixelLuma function in MagickCore/pixel-accessor.h.

## References
- https://usn.ubuntu.com/3681-1/
- http://www.securityfocus.com/bid/100013
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2018/dsa-4204
- https://github.com/ImageMagick/ImageMagick/issues/588
