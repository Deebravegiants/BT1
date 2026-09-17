# [M] CVE-2016-8691

## Summary
Severity: Medium
Advisory: CVE-2016-8691
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8691
Type: osv

## Details
The jpc_dec_process_siz function in libjasper/jpc/jpc_dec.c in JasPer before 1.900.4 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted XRsiz value in a BMP image to the imginfo command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THLEZURI4D24PRM7SMASC5I25IAWXXTM/
- http://www.debian.org/security/2017/dsa-3785
- http://www.openwall.com/lists/oss-security/2016/08/23/6
- http://www.openwall.com/lists/oss-security/2016/10/16/14
- http://www.securityfocus.com/bid/93593
- https://access.redhat.com/errata/RHSA-2017:1208
- https://blogs.gentoo.org/ago/2016/10/16/jasper-two-divide-by-zero-in-jpc_dec_process_siz-jpc_dec-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1385502
- https://github.com/mdadams/jasper/commit/d8c2604cd438c41ec72aff52c16ebd8183068020
