# [H] CVE-2016-3624

## Summary
Severity: High
Advisory: CVE-2016-3624
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-3624
Type: osv

## Details
The cvtClump function in the rgb2ycbcr tool in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds write) by setting the "-v" option to -1.

## References
- http://www.debian.org/security/2017/dsa-3762
- http://www.securityfocus.com/bid/85956
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2568
- http://www.openwall.com/lists/oss-security/2016/04/08/4
