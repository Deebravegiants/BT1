# [M] CVE-2017-13140

## Summary
Severity: Medium
Advisory: CVE-2017-13140
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13140
Type: osv

## Details
In ImageMagick before 6.9.9-1 and 7.x before 7.0.6-2, the ReadOnePNGImage function in coders/png.c allows remote attackers to cause a denial of service (application hang in LockSemaphoreInfo) via a PNG file with a width equal to MAGICK_WIDTH_LIMIT.

## References
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870111
- https://github.com/ImageMagick/ImageMagick/issues/596
