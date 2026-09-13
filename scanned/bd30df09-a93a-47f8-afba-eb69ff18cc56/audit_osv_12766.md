# [M] CVE-2018-14662

## Summary
Severity: Medium
Advisory: CVE-2018-14662
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2018-14662
Type: osv

## Details
It was found Ceph versions before 13.2.4 that authenticated ceph users with read only permissions could steal dm-crypt encryption keys used in ceph disk encryption.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00100.html
- https://access.redhat.com/errata/RHSA-2019:2538
- https://access.redhat.com/errata/RHSA-2019:2541
- https://ceph.com/releases/13-2-4-mimic-released
- https://lists.debian.org/debian-lts-announce/2019/03/msg00002.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00013.html
- https://usn.ubuntu.com/4035-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14662
