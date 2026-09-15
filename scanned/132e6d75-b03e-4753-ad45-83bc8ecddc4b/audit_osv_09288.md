# [M] CVE-2016-9395

## Summary
Severity: Medium
Advisory: CVE-2016-9395
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9395
Type: osv

## Details
The jas_seq2d_create function in jas_seq.c in JasPer before 1.900.25 allows remote attackers to cause a denial of service (assertion failure) via a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00009.html
- http://www.openwall.com/lists/oss-security/2016/11/17/1
- http://www.securityfocus.com/bid/94376
- https://blogs.gentoo.org/ago/2016/11/16/jasper-multiple-assertion-failure
- https://bugzilla.redhat.com/show_bug.cgi?id=1396977
- https://github.com/mdadams/jasper/commit/d42b2388f7f8e0332c846675133acea151fc557a
