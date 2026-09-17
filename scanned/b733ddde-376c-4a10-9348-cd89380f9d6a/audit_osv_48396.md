# [H] CVE-2017-7263

## Summary
Severity: High
Advisory: CVE-2017-7263
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-26
Source: https://osv.dev/vulnerability/CVE-2017-7263
Type: osv

## Details
The bm_readbody_bmp function in bitmap_io.c in Potrace 1.14 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact via a crafted BMP image. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-8698.

## References
- http://www.securityfocus.com/bid/97112
- https://blogs.gentoo.org/ago/2017/03/03/potrace-heap-based-buffer-overflow-in-bm_readbody_bmp-bitmap_io-c-incomplete-fix-for-cve-2016-8698/
