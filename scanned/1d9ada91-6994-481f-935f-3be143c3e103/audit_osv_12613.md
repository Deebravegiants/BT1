# [H] CVE-2018-13405

## Summary
Severity: High
Advisory: CVE-2018-13405
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-13405
Type: osv

## Details
The inode_init_owner function in fs/inode.c in the Linux kernel through 3.16 allows local users to create files with an unintended group ownership, in a scenario where a directory is SGID to a certain group and is writable by a user who is not a member of that group. Here, the non-member can trigger creation of a plain file whose group ownership is that group. The intended behavior was that the non-member can trigger creation of a directory (but not a plain file) whose group ownership is that group. The non-member can escalate privileges by making the plain file executable and SGID.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRBNBX73SAFKQWBOX76SLMWPTKJPVGEJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTKKIAUMR5FAYLZ7HLEPOXMKAAE3BYBQ/
- http://www.securityfocus.com/bid/106503
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2019:4164
- https://lists.debian.org/debian-lts-announce/2018/08/msg00014.html
- https://support.f5.com/csp/article/K00854051
- https://usn.ubuntu.com/3753-2/
- https://www.debian.org/security/2018/dsa-4266
- https://access.redhat.com/errata/RHSA-2019:2730
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3754-1/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2019:2566
- https://access.redhat.com/errata/RHSA-2019:2696
- https://twitter.com/grsecurity/status/1015082951204327425
- https://usn.ubuntu.com/3752-1/
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2019:0717
