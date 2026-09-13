# [M] CVE-2016-10267

## Summary
Severity: Medium
Advisory: CVE-2016-10267
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10267
Type: osv

## Details
LibTIFF 4.0.7 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted TIFF image, related to libtiff/tif_ojpeg.c:816:8.

## References
- http://www.securityfocus.com/bid/97117
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-divide-by-zero
- https://github.com/vadz/libtiff/commit/43bc256d8ae44b92d2734a3c5bc73957a4d7c1ec
