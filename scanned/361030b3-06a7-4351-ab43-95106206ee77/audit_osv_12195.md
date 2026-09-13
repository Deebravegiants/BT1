# [H] CVE-2018-10873

## Summary
Severity: High
Advisory: CVE-2018-10873
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/CVE-2018-10873
Type: osv

## Details
A vulnerability was discovered in SPICE before version 0.14.1 where the generated code used for demarshalling messages lacked sufficient bounds checks. A malicious client or server, after authentication, could send specially crafted messages to its peer which would result in a crash or, potentially, other impacts.

## References
- http://www.securityfocus.com/bid/105152
- https://access.redhat.com/errata/RHSA-2018:2731
- https://access.redhat.com/errata/RHSA-2018:2732
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/08/msg00035.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00037.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00038.html
- https://usn.ubuntu.com/3751-1/
- https://www.debian.org/security/2018/dsa-4319
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10873
- https://gitlab.freedesktop.org/spice/spice-common/commit/bb15d4815ab586b4c4a20f4a565970a44824c42c
