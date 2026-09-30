# [M] CVE-2016-9532

## Summary
Severity: Medium
Advisory: CVE-2016-9532
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-9532
Type: osv

## Details
Integer overflow in the writeBufferToSeparateStrips function in tiffcrop.c in LibTIFF before 4.0.7 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted tif file.

## References
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/11/11/14
- http://www.openwall.com/lists/oss-security/2016/11/21/1
- http://www.openwall.com/lists/oss-security/2016/11/22/1
- http://www.securityfocus.com/bid/94424
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2592
- https://bugzilla.redhat.com/show_bug.cgi?id=1397726
