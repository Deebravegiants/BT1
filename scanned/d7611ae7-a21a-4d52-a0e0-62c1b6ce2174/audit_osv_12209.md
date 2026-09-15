# [H] CVE-2018-10911

## Summary
Severity: High
Advisory: CVE-2018-10911
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10911
Type: osv

## Details
A flaw was found in the way dic_unserialize function of glusterfs does not handle negative key length values. An attacker could use this flaw to read memory from other locations into the stored dict value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:2892
- https://access.redhat.com/errata/RHSA-2018:3242
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10911
- https://review.gluster.org/#/c/glusterfs/+/21067/
