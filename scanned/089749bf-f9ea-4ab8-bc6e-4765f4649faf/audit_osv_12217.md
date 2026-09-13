# [H] CVE-2018-10923

## Summary
Severity: High
Advisory: CVE-2018-10923
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10923
Type: osv

## Details
It was found that the "mknod" call derived from mknod(2) can create files pointing to devices on a glusterfs server node. An authenticated attacker could use this to create an arbitrary device and read data from any device attached to the glusterfs server node.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10923
