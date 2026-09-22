# [M] CVE-2016-10208

## Summary
Severity: Medium
Advisory: CVE-2016-10208
CVSS: 4.3 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2016-10208
Type: osv

## Details
The ext4_fill_super function in fs/ext4/super.c in the Linux kernel through 4.9.8 does not properly validate meta block groups, which allows physically proximate attackers to cause a denial of service (out-of-bounds read and system crash) via a crafted ext4 image.

## References
- http://www.securityfocus.com/bid/94354
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://seclists.org/fulldisclosure/2016/Nov/75
- https://access.redhat.com/errata/RHSA-2017:1297
- https://access.redhat.com/errata/RHSA-2017:1298
- https://access.redhat.com/errata/RHSA-2017:1308
- http://www.openwall.com/lists/oss-security/2017/02/05/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1395190
- https://github.com/torvalds/linux/commit/3a4b77cd47bb837b8557595ec7425f281f2ca1fe
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3a4b77cd47bb837b8557595ec7425f281f2ca1fe
