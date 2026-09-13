# [M] CVE-2019-6133

## Summary
Severity: Medium
Advisory: CVE-2019-6133
CVSS: 6.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6133
Type: osv

## Details
In PolicyKit (aka polkit) 0.115, the "start time" protection mechanism can be bypassed because fork() is not atomic, and therefore authorization decisions are improperly cached. This is related to lack of uid checking in polkitbackend/polkitbackendinteractiveauthority.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00049.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://usn.ubuntu.com/3934-2/
- http://www.securityfocus.com/bid/106537
- https://access.redhat.com/errata/RHSA-2019:0230
- https://access.redhat.com/errata/RHSA-2019:0420
- https://access.redhat.com/errata/RHSA-2019:0832
- https://access.redhat.com/errata/RHSA-2019:2699
- https://access.redhat.com/errata/RHSA-2019:2978
- https://lists.debian.org/debian-lts-announce/2019/01/msg00021.html
- https://support.f5.com/csp/article/K22715344
- https://usn.ubuntu.com/3901-1/
- https://usn.ubuntu.com/3901-2/
- https://usn.ubuntu.com/3903-1/
- https://usn.ubuntu.com/3903-2/
- https://usn.ubuntu.com/3908-1/
- https://usn.ubuntu.com/3908-2/
- https://usn.ubuntu.com/3910-1/
- https://usn.ubuntu.com/3910-2/
