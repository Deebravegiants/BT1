# [M] CVE-2016-8690

## Summary
Severity: Medium
Advisory: CVE-2016-8690
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8690
Type: osv

## Details
The bmp_getdata function in libjasper/bmp/bmp_dec.c in JasPer before 1.900.5 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted BMP image in an imginfo command.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22FCKKHQCQ3S6TZY5G44EFDTMWOJXJRD/
- http://www.openwall.com/lists/oss-security/2016/08/23/6
- http://www.openwall.com/lists/oss-security/2016/10/16/14
- http://www.securityfocus.com/bid/93590
- https://access.redhat.com/errata/RHSA-2017:1208
- https://blogs.gentoo.org/ago/2016/10/16/jasper-two-null-pointer-dereference-in-bmp_getdata-bmp_dec-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385499
- https://github.com/mdadams/jasper/commit/8f62b4761711d036fd8964df256b938c809b7fca
