# [M] CVE-2016-9392

## Summary
Severity: Medium
Advisory: CVE-2016-9392
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9392
Type: osv

## Details
The calcstepsizes function in jpc_dec.c in JasPer before 1.900.17 allows remote attackers to cause a denial of service (assertion failure) via a crafted file.

## References
- https://usn.ubuntu.com/3693-1/
- http://www.securityfocus.com/bid/94377
- https://access.redhat.com/errata/RHSA-2017:1208
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- http://www.openwall.com/lists/oss-security/2016/11/17/1
- https://blogs.gentoo.org/ago/2016/11/16/jasper-multiple-assertion-failure
- https://bugzilla.redhat.com/show_bug.cgi?id=1396971
- https://github.com/mdadams/jasper/commit/f7038068550fba0e41e1d0c355787f1dcd5bf330
