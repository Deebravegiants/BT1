# [C] CVE-2017-13139

## Summary
Severity: Critical
Advisory: CVE-2017-13139
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13139
Type: osv

## Details
In ImageMagick before 6.9.9-0 and 7.x before 7.0.6-1, the ReadOneMNGImage function in coders/png.c has an out-of-bounds read with the MNG CLIP chunk.

## References
- http://www.securityfocus.com/bid/100494
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870109
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2017/dsa-4040
- https://github.com/ImageMagick/ImageMagick/commit/d072ed6aff835c174e856ce3a428163c0da9e8f4
