# [M] CVE-2016-8885

## Summary
Severity: Medium
Advisory: CVE-2016-8885
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-8885
Type: osv

## Details
The bmp_getdata function in libjasper/bmp/bmp_dec.c in JasPer before 1.900.9 allows remote attackers to cause a denial of service (NULL pointer dereference) by calling the imginfo command with a crafted BMP image.

## References
- http://www.openwall.com/lists/oss-security/2016/10/23/1
- http://www.openwall.com/lists/oss-security/2016/10/23/5
- http://www.openwall.com/lists/oss-security/2016/10/23/9
- http://www.securityfocus.com/bid/93834
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22FCKKHQCQ3S6TZY5G44EFDTMWOJXJRD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EGI2FZQLOTSZI3VA4ECJERI74SMNQDL4/
- https://access.redhat.com/errata/RHSA-2017:1208
- https://bugzilla.redhat.com/show_bug.cgi?id=1385499
- https://blogs.gentoo.org/ago/2016/10/18/jasper-two-null-pointer-dereference-in-bmp_getdata-bmp_dec-c-incomplete-fix-for-cve-2016-8690
