# [M] CVE-2016-5316

## Summary
Severity: Medium
Advisory: CVE-2016-5316
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/CVE-2016-5316
Type: osv

## Details
Out-of-bounds read in the PixarLogCleanup function in tif_pixarlog.c in libtiff 4.0.6 and earlier allows remote attackers to crash the application by sending a crafted TIFF image to the rgb2ycbcr tool.

## References
- http://www.securityfocus.com/bid/91203
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00087.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00060.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00090.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/06/15/3
- https://security.gentoo.org/glsa/201701-16
