# [M] CVE-2015-1339

## Summary
Severity: Medium
Advisory: CVE-2015-1339
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-1339
Type: osv

## Details
Memory leak in the cuse_channel_release function in fs/fuse/cuse.c in the Linux kernel before 4.4 allows local users to cause a denial of service (memory consumption) or possibly have unspecified other impact by opening /dev/cuse many times.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- https://github.com/torvalds/linux/commit/2c5816b4beccc8ba709144539f6fdd764f8fa49c
- http://www.openwall.com/lists/oss-security/2016/03/02/13
- https://github.com/torvalds/linux/commit/2c5816b4beccc8ba709144539f6fdd764f8fa49c
- https://bugzilla.novell.com/show_bug.cgi?id=969356
- https://bugzilla.redhat.com/show_bug.cgi?id=1314331
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2c5816b4beccc8ba709144539f6fdd764f8fa49c
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- https://security-tracker.debian.org/tracker/CVE-2015-1339
