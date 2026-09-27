# [M] CVE-2016-8695

## Summary
Severity: Medium
Advisory: CVE-2016-8695
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-31
Source: https://osv.dev/vulnerability/CVE-2016-8695
Type: osv

## Details
The bm_readbody_bmp function in bitmap_io.c in potrace before 1.13 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted BMP image, a different vulnerability than CVE-2016-8694 and CVE-2016-8696.

## References
- http://www.openwall.com/lists/oss-security/2016/10/16/12
- http://www.securityfocus.com/bid/93778
- https://blogs.gentoo.org/ago/2016/08/08/potrace-multiple-three-null-pointer-dereference-in-bm_readbody_bmp-bitmap_io-c/
- http://potrace.sourceforge.net/ChangeLog
- http://www.openwall.com/lists/oss-security/2016/08/18/11
