# [H] CVE-2018-10904

## Summary
Severity: High
Advisory: CVE-2018-10904
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10904
Type: osv

## Details
It was found that glusterfs server does not properly sanitize file paths in the "trusted.io-stats-dump" extended attribute which is used by the "debug/io-stats" translator. Attacker can use this flaw to create files and execute arbitrary code. To exploit this attacker would require sufficient access to modify the extended attributes of files on a gluster volume.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://access.redhat.com/errata/RHSA-2018:2607
- https://access.redhat.com/errata/RHSA-2018:2608
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/09/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10904
- https://review.gluster.org/#/c/glusterfs/+/21072/
