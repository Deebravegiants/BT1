# [M] CVE-2016-9685

## Summary
Severity: Medium
Advisory: CVE-2016-9685
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9685
Type: osv

## Details
Multiple memory leaks in error paths in fs/xfs/xfs_attr_list.c in the Linux kernel before 4.5.1 allow local users to cause a denial of service (memory consumption) via crafted XFS filesystem operations.

## References
- http://www.securityfocus.com/bid/94593
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://bugzilla.redhat.com/show_bug.cgi?id=1396941
- https://github.com/torvalds/linux/commit/2e83b79b2d6c78bf1b4aa227938a214dcbddc83f
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2e83b79b2d6c78bf1b4aa227938a214dcbddc83f
- http://www.openwall.com/lists/oss-security/2016/11/30/1
