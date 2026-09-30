# [M] CVE-2015-8839

## Summary
Severity: Medium
Advisory: CVE-2015-8839
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2015-8839
Type: osv

## Details
Multiple race conditions in the ext4 filesystem implementation in the Linux kernel before 4.5 allow local users to cause a denial of service (disk corruption) by writing to a page that is associated with a different user's file after unsynchronized hole punching and page-fault handling.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ea3d7209ca01da209cda6f0dea8be9cc4b7a933b
- http://www.openwall.com/lists/oss-security/2016/04/01/4
- http://www.securityfocus.com/bid/85798
- http://www.securitytracker.com/id/1035455
- http://www.ubuntu.com/usn/USN-3005-1
- http://www.ubuntu.com/usn/USN-3006-1
- http://www.ubuntu.com/usn/USN-3007-1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- https://bugzilla.redhat.com/show_bug.cgi?id=1323577
- https://github.com/torvalds/linux/commit/ea3d7209ca01da209cda6f0dea8be9cc4b7a933b
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- http://www.openwall.com/lists/oss-security/2016/04/01/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1323577
