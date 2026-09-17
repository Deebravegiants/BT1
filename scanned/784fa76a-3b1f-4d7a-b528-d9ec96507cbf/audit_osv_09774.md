# [M] CVE-2017-11448

## Summary
Severity: Medium
Advisory: CVE-2017-11448
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11448
Type: osv

## Details
The ReadJPEGImage function in coders/jpeg.c in ImageMagick before 7.0.6-1 allows remote attackers to obtain sensitive information from uninitialized memory locations via a crafted file.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=867893
- https://github.com/ImageMagick/ImageMagick/commit/f6463ca9588579633bbaed9460899d892aa3c64a
- https://github.com/ImageMagick/ImageMagick/issues/556
