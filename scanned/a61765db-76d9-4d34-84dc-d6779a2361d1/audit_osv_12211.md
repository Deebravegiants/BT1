# [M] CVE-2018-10913

## Summary
Severity: Medium
Advisory: CVE-2018-10913
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10913
Type: osv

## Details
An information disclosure vulnerability was discovered in glusterfs server. An attacker could issue a xattr request via glusterfs FUSE to determine the existence of any file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10913
- https://review.gluster.org/#/c/glusterfs/+/21071/
