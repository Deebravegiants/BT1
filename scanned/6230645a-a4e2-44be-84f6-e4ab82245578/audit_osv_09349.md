# [M] CVE-2016-9559

## Summary
Severity: Medium
Advisory: CVE-2016-9559
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2016-9559
Type: osv

## Details
coders/tiff.c in ImageMagick before 7.0.3.7 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted image.

## References
- http://www.debian.org/security/2016/dsa-3726
- http://www.openwall.com/lists/oss-security/2016/11/23/4
- http://www.securityfocus.com/bid/94489
- http://www.openwall.com/lists/oss-security/2016/11/19/7
- https://blogs.gentoo.org/ago/2016/11/19/imagemagick-null-pointer-must-never-be-null-tiff-c/
- https://github.com/ImageMagick/ImageMagick/commit/b61d35eaccc0a7ddeff8a1c3abfcd0a43ccf210b
- https://github.com/ImageMagick/ImageMagick/issues/298
