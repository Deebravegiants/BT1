# [H] CVE-2016-10270

## Summary
Severity: High
Advisory: CVE-2016-10270
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10270
Type: osv

## Details
LibTIFF 4.0.7 allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted TIFF image, related to "READ of size 8" and libtiff/tif_read.c:523:22.

## References
- http://www.securityfocus.com/bid/97200
- http://www.debian.org/security/2017/dsa-3844
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-heap-based-buffer-overflow/
- https://github.com/vadz/libtiff/commit/9a72a69e035ee70ff5c41541c8c61cd97990d018
