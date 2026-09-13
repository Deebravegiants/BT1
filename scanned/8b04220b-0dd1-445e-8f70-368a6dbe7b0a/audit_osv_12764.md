# [M] CVE-2018-14660

## Summary
Severity: Medium
Advisory: CVE-2018-14660
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2018-14660
Type: osv

## Details
A flaw was found in glusterfs server through versions 4.1.4 and 3.1.2 which allowed repeated usage of GF_META_LOCK_KEY xattr. A remote, authenticated attacker could use this flaw to create multiple locks for single inode by using setxattr repetitively resulting in memory exhaustion of glusterfs server node.

## References
- https://access.redhat.com/errata/RHSA-2018:3431
- https://access.redhat.com/errata/RHSA-2018:3432
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14660
