# [M] CVE-2018-20534

## Summary
Severity: Medium
Advisory: CVE-2018-20534
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20534
Type: osv

## Details
There is an illegal address access at ext/testcase.c in libsolv.a in libsolv through 0.7.2 that will cause a denial of service. NOTE: third parties dispute this issue stating that the issue affects the test suite and not the underlying library. It cannot be exploited in any real-world application

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00057.html
- https://access.redhat.com/errata/RHSA-2019:2290
- https://access.redhat.com/errata/RHSA-2019:3583
- https://usn.ubuntu.com/3916-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1652604
- https://bugzilla.suse.com/show_bug.cgi?id=1120631
- https://github.com/openSUSE/libsolv/pull/291
