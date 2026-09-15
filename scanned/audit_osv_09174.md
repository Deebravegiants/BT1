# [H] CVE-2016-8693

## Summary
Severity: High
Advisory: CVE-2016-8693
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8693
Type: osv

## Details
Double free vulnerability in the mem_close function in jas_stream.c in JasPer before 1.900.10 allows remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via a crafted BMP image to the imginfo command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22FCKKHQCQ3S6TZY5G44EFDTMWOJXJRD/
- http://lists.opensuse.org/opensuse-updates/2016-11/msg00010.html
- http://www.debian.org/security/2017/dsa-3785
- http://www.openwall.com/lists/oss-security/2016/08/23/6
- http://www.openwall.com/lists/oss-security/2016/10/16/14
- http://www.securityfocus.com/bid/93587
- https://access.redhat.com/errata/RHSA-2017:1208
- https://blogs.gentoo.org/ago/2016/10/16/jasper-double-free-in-mem_close-jas_stream-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385507
- https://github.com/mdadams/jasper/commit/44a524e367597af58d6265ae2014468b334d0309
