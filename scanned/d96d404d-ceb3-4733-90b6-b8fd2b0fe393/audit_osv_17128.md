# [M] CVE-2020-12770

## Summary
Severity: Medium
Advisory: CVE-2020-12770
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12770
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.6.11. sg_write lacks an sg_remove_request call in a certain failure case, aka CID-83c6f2390040.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ES5C6ZCMALBEBMKNNCTBSLLSYGFZG3FF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R54VC7B6MDYKP57AWC2HN7AUJYH62RKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IO5XIQSRI747P4RVVTNX7TUPEOCF4OPU/
- https://usn.ubuntu.com/4411-1/
- https://www.debian.org/security/2020/dsa-4698
- https://usn.ubuntu.com/4412-1/
- https://usn.ubuntu.com/4414-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://www.debian.org/security/2020/dsa-4699
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4413-1/
- https://usn.ubuntu.com/4419-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=83c6f2390040f188cc25b270b4befeb5628c1aee
- https://lkml.org/lkml/2020/4/13/870
