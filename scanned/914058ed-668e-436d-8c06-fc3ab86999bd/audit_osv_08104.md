# [M] CVE-2016-10266

## Summary
Severity: Medium
Advisory: CVE-2016-10266
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10266
Type: osv

## Details
LibTIFF 4.0.7 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted TIFF image, related to libtiff/tif_read.c:351:22.

## References
- http://www.securityfocus.com/bid/97115
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-divide-by-zero
- https://github.com/vadz/libtiff/commit/438274f938e046d33cb0e1230b41da32ffe223e1
