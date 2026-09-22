# [M] CVE-2015-8953

## Summary
Severity: Medium
Advisory: CVE-2015-8953
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2015-8953
Type: osv

## Details
fs/overlayfs/copy_up.c in the Linux kernel before 4.2.6 uses an incorrect cleanup code path, which allows local users to cause a denial of service (dentry reference leak) via filesystem operations on a large file in a lower overlayfs layer.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ab79efab0a0ba01a74df782eb7fa44b044dae8b5
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.6
- http://www.openwall.com/lists/oss-security/2016/08/23/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1367814
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ab79efab0a0ba01a74df782eb7fa44b044dae8b5
- http://www.openwall.com/lists/oss-security/2016/08/23/9
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ab79efab0a0ba01a74df782eb7fa44b044dae8b5
- https://github.com/torvalds/linux/commit/ab79efab0a0ba01a74df782eb7fa44b044dae8b5
- https://bugzilla.redhat.com/show_bug.cgi?id=1367814
- http://www.securityfocus.com/bid/92611
