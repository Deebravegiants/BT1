# [M] CVE-2014-9717

## Summary
Severity: Medium
Advisory: CVE-2014-9717
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2014-9717
Type: osv

## Details
fs/namespace.c in the Linux kernel before 4.0.2 processes MNT_DETACH umount2 system calls without verifying that the MNT_LOCKED flag is unset, which allows local users to bypass intended access restrictions and navigate to filesystem locations beneath a mount by calling umount2 within a user namespace.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ce07d891a0891d3c0d0c2d73d577490486b809e1
- https://github.com/torvalds/linux/commit/ce07d891a0891d3c0d0c2d73d577490486b809e1
- https://bugzilla.redhat.com/show_bug.cgi?id=1226751
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.2
- http://www.openwall.com/lists/oss-security/2015/04/17/4
- http://www.securityfocus.com/bid/74226
- http://www.spinics.net/lists/linux-containers/msg30786.html
- https://groups.google.com/forum/message/raw?msg=linux.kernel/HnegnbXk0Vs/RClojwJzAFEJ
