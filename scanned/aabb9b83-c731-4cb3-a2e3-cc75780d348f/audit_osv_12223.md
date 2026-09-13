# [M] CVE-2018-10930

## Summary
Severity: Medium
Advisory: CVE-2018-10930
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10930
Type: osv

## Details
A flaw was found in RPC request using gfs3_rename_req in glusterfs server. An authenticated attacker could use this flaw to write to a destination outside the gluster volume.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10930
- https://review.gluster.org/#/c/glusterfs/+/21068/
