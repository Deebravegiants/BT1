# [M] CVE-2017-13141

## Summary
Severity: Medium
Advisory: CVE-2017-13141
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13141
Type: osv

## Details
In ImageMagick before 6.9.9-4 and 7.x before 7.0.6-4, a crafted file could trigger a memory leak in ReadOnePNGImage in coders/png.c.

## References
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870116
- https://github.com/ImageMagick/ImageMagick/issues/600
