# [M] CVE-2017-13142

## Summary
Severity: Medium
Advisory: CVE-2017-13142
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13142
Type: osv

## Details
In ImageMagick before 6.9.9-0 and 7.x before 7.0.6-1, a crafted PNG file could trigger a crash because there was an insufficient check for short files.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://usn.ubuntu.com/3681-1/
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870105
- https://github.com/ImageMagick/ImageMagick/commit/46e3aabbf8d59a1bdebdbb65acb9b9e0484577d3
- https://github.com/ImageMagick/ImageMagick/commit/aa84944b405acebbeefe871d0f64969b9e9f31ac
