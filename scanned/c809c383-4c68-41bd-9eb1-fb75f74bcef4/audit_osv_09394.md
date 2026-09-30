# [M] CVE-2016-9773

## Summary
Severity: Medium
Advisory: CVE-2016-9773
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-9773
Type: osv

## Details
Heap-based buffer overflow in the IsPixelGray function in MagickCore/pixel-accessor.h in ImageMagick 7.0.3.8 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a crafted image file.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-9556.

## References
- http://www.openwall.com/lists/oss-security/2016/12/01/4
- http://www.openwall.com/lists/oss-security/2016/12/02/11
- http://www.openwall.com/lists/oss-security/2016/12/02/12
- https://blogs.gentoo.org/ago/2016/12/01/imagemagick-heap-based-buffer-overflow-in-ispixelgray-pixel-accessor-h-incomplete-fix-for-cve-2016-9556/
