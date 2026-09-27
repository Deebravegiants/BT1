# [H] CVE-2017-13146

## Summary
Severity: High
Advisory: CVE-2017-13146
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13146
Type: osv

## Details
In ImageMagick before 6.9.8-5 and 7.x before 7.0.5-6, there is a memory leak in the ReadMATImage function in coders/mat.c.

## References
- https://security.gentoo.org/glsa/201711-07
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870013
- https://github.com/ImageMagick/ImageMagick/commit/79e5dbcdd1fc2f714f9bae548bc55d5073f3ed20
