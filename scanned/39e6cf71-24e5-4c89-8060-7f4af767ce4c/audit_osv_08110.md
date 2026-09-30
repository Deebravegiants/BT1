# [H] CVE-2016-10272

## Summary
Severity: High
Advisory: CVE-2016-10272
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10272
Type: osv

## Details
LibTIFF 4.0.7 allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a crafted TIFF image, related to "WRITE of size 2048" and libtiff/tif_next.c:64:9.

## References
- http://www.securityfocus.com/bid/97197
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-heap-based-buffer-overflow/
- https://github.com/vadz/libtiff/commit/9657bbe3cdce4aaa90e07d50c1c70ae52da0ba6a
