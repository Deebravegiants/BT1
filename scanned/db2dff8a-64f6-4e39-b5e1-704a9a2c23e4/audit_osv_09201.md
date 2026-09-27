# [M] CVE-2016-8887

## Summary
Severity: Medium
Advisory: CVE-2016-8887
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-8887
Type: osv

## Details
The jp2_colr_destroy function in libjasper/jp2/jp2_cod.c in JasPer before 1.900.10 allows remote attackers to cause a denial of service (NULL pointer dereference).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22FCKKHQCQ3S6TZY5G44EFDTMWOJXJRD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EGI2FZQLOTSZI3VA4ECJERI74SMNQDL4/
- https://usn.ubuntu.com/3693-1/
- http://www.openwall.com/lists/oss-security/2016/10/23/3
- http://www.openwall.com/lists/oss-security/2016/10/23/6
- http://www.securityfocus.com/bid/93835
- https://blogs.gentoo.org/ago/2016/10/18/jasper-null-pointer-dereference-in-jp2_colr_destroy-jp2_cod-c
- https://bugzilla.redhat.com/show_bug.cgi?id=1388828
- https://github.com/mdadams/jasper/commit/e24bdc716c3327b067c551bc6cfb97fd2370358d
