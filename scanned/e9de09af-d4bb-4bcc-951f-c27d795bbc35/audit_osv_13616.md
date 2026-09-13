# [M] CVE-2018-20533

## Summary
Severity: Medium
Advisory: CVE-2018-20533
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20533
Type: osv

## Details
There is a NULL pointer dereference at ext/testcase.c (function testcase_str2dep_complex) in libsolvext.a in libsolv through 0.7.2 that will cause a denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00057.html
- https://access.redhat.com/errata/RHSA-2019:2290
- https://usn.ubuntu.com/3916-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1652599
- https://github.com/openSUSE/libsolv/pull/291
