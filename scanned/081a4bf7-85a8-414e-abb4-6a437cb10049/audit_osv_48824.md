# [M] CVE-2018-14654

## Summary
Severity: Medium
Advisory: CVE-2018-14654
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-14654
Type: osv

## Details
The Gluster file system through version 4.1.4 is vulnerable to abuse of the 'features/index' translator. A remote attacker with access to mount volumes could exploit this via the 'GF_XATTROP_ENTRY_IN_KEY' xattrop to create arbitrary, empty files on the target server.

## References
- https://access.redhat.com/errata/RHSA-2018:3432
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://access.redhat.com/errata/RHSA-2018:3431
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14654
