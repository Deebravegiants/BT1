# [M] CVE-2016-9557

## Summary
Severity: Medium
Advisory: CVE-2016-9557
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9557
Type: osv

## Details
Integer overflow in jas_image.c in JasPer before 1.900.25 allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2016/11/23/2
- http://www.securityfocus.com/bid/94490
- https://blogs.gentoo.org/ago/2016/11/19/jasper-signed-integer-overflow-in-jas_image-c
- https://bugzilla.redhat.com/show_bug.cgi?id=1398251
- https://github.com/mdadams/jasper/commit/d42b2388f7f8e0332c846675133acea151fc557a
