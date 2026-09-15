# [M] CVE-2016-9390

## Summary
Severity: Medium
Advisory: CVE-2016-9390
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9390
Type: osv

## Details
The jas_seq2d_create function in jas_seq.c in JasPer before 1.900.14 allows remote attackers to cause a denial of service (assertion failure) via a crafted image file.

## References
- https://usn.ubuntu.com/3693-1/
- http://www.openwall.com/lists/oss-security/2016/11/17/1
- http://www.securityfocus.com/bid/94371
- https://access.redhat.com/errata/RHSA-2017:1208
- https://blogs.gentoo.org/ago/2016/11/16/jasper-multiple-assertion-failure
- https://bugzilla.redhat.com/show_bug.cgi?id=1396965
- https://github.com/mdadams/jasper/commit/ba2b9d000660313af7b692542afbd374c5685865
