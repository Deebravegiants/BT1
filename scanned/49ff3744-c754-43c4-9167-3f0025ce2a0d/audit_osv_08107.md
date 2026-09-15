# [H] CVE-2016-10269

## Summary
Severity: High
Advisory: CVE-2016-10269
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10269
Type: osv

## Details
LibTIFF 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6 and 4.0.7 allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted TIFF image, related to "READ of size 512" and libtiff/tif_unix.c:340:2.

## References
- http://www.securityfocus.com/bid/97201
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2016-10269
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-heap-based-buffer-overflow/
- https://github.com/vadz/libtiff/commit/1044b43637fa7f70fb19b93593777b78bd20da86
