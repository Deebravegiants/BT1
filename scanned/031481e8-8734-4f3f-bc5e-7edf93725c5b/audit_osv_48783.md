# [M] CVE-2018-13099

## Summary
Severity: Medium
Advisory: CVE-2018-13099
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13099
Type: osv

## Details
An issue was discovered in fs/f2fs/inline.c in the Linux kernel through 4.4. A denial of service (out-of-bounds memory access and BUG) can occur for a modified f2fs filesystem image in which an inline inode contains an invalid reserved blkaddr.

## References
- http://www.securityfocus.com/bid/104680
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- https://www.debian.org/security/2018/dsa-4308
- http://lists.opensuse.org/opensuse-security-announce/2018-10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://seclists.org/bugtraq/2018/Oct/4
- https://usn.ubuntu.com/3932-1/
- http://packetstormsecurity.com/files/151420/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://bugzilla.kernel.org/show_bug.cgi?id=200179
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4dbe38dc386910c668c75ae616b99b823b59f3eb
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=3bfe2049c222b23342ff2a216cd5a869e8a14897
- https://seclists.org/bugtraq/2019/Jan/52
- https://sourceforge.net/p/linux-f2fs/mailman/message/36356878/
