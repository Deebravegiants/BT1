# [M] CVE-2016-9273

## Summary
Severity: Medium
Advisory: CVE-2016-9273
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-9273
Type: osv

## Details
tiffsplit in libtiff 4.0.6 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted file, related to changing td_nstrips in TIFF_STRIPCHOP mode.

## References
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/11/09/20
- http://www.openwall.com/lists/oss-security/2016/11/11/6
- http://www.securityfocus.com/bid/94271
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2587
