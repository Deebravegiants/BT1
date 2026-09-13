# [M] CVE-2016-10741

## Summary
Severity: Medium
Advisory: CVE-2016-10741
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-01
Source: https://osv.dev/vulnerability/CVE-2016-10741
Type: osv

## Details
In the Linux kernel before 4.9.3, fs/xfs/xfs_aops.c allows local users to cause a denial of service (system crash) because there is a race condition between direct and memory-mapped I/O (associated with a hole) that is handled with BUG_ON instead of an I/O failure.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- http://www.securityfocus.com/bid/106822
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.3
- https://bugzilla.suse.com/show_bug.cgi?id=1124010
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=04197b341f23b908193308b8d63d17ff23232598
- https://github.com/torvalds/linux/commit/04197b341f23b908193308b8d63d17ff23232598
