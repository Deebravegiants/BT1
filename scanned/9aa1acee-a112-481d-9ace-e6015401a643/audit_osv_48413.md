# [M] CVE-2017-7495

## Summary
Severity: Medium
Advisory: CVE-2017-7495
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-15
Source: https://osv.dev/vulnerability/CVE-2017-7495
Type: osv

## Details
fs/ext4/inode.c in the Linux kernel before 4.6.2, when ext4 data=ordered mode is used, mishandles a needs-flushing-before-commit list, which allows local users to obtain sensitive information from other users' files in opportunistic circumstances by waiting for a hardware reset, creating a new file, making write system calls, and reading this file.

## References
- https://source.android.com/security/bulletin/2017-09-01
- http://www.securityfocus.com/bid/98491
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.2
- https://bugzilla.redhat.com/show_bug.cgi?id=1450261
- https://github.com/torvalds/linux/commit/06bd3c36a733ac27962fea7d6f47168841376824
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=06bd3c36a733ac27962fea7d6f47168841376824
- http://www.openwall.com/lists/oss-security/2017/05/15/2
