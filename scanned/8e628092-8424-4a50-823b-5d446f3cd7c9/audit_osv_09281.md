# [M] CVE-2016-9388

## Summary
Severity: Medium
Advisory: CVE-2016-9388
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9388
Type: osv

## Details
The ras_getcmap function in ras_dec.c in JasPer before 1.900.14 allows remote attackers to cause a denial of service (assertion failure) via a crafted image file.

## References
- http://www.securityfocus.com/bid/94371
- https://access.redhat.com/errata/RHSA-2017:1208
- https://usn.ubuntu.com/3693-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1396962
- http://www.openwall.com/lists/oss-security/2016/11/17/1
- https://blogs.gentoo.org/ago/2016/11/16/jasper-multiple-assertion-failure
- https://github.com/mdadams/jasper/commit/411a4068f8c464e883358bf403a3e25158863823
