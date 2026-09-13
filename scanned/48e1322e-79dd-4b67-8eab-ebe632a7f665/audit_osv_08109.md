# [H] CVE-2016-10271

## Summary
Severity: High
Advisory: CVE-2016-10271
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10271
Type: osv

## Details
tools/tiffcrop.c in LibTIFF 4.0.7 allows remote attackers to cause a denial of service (heap-based buffer over-read and buffer overflow) or possibly have unspecified other impact via a crafted TIFF image, related to "READ of size 1" and libtiff/tif_fax3.c:413:13.

## References
- http://www.securityfocus.com/bid/97199
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-heap-based-buffer-overflow/
- https://github.com/vadz/libtiff/commit/9657bbe3cdce4aaa90e07d50c1c70ae52da0ba6a
