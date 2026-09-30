# [M] CVE-2016-9556

## Summary
Severity: Medium
Advisory: CVE-2016-9556
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9556
Type: osv

## Details
The IsPixelGray function in MagickCore/pixel-accessor.h in ImageMagick 7.0.3-8 allows remote attackers to cause a denial of service (out-of-bounds heap read) via a crafted image file.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00040.html
- http://www.debian.org/security/2016/dsa-3726
- http://www.openwall.com/lists/oss-security/2016/11/23/1
- http://www.openwall.com/lists/oss-security/2016/12/01/4
- http://www.openwall.com/lists/oss-security/2016/12/02/12
- http://www.securityfocus.com/bid/94492
- https://blogs.gentoo.org/ago/2016/11/19/imagemagick-heap-based-buffer-overflow-in-ispixelgray-pixel-accessor-h
- https://bugzilla.redhat.com/show_bug.cgi?id=1398198
- https://github.com/ImageMagick/ImageMagick/commit/ce98a7acbcfca7f0a178f4b1e7b957e419e0cc99
