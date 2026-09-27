# [M] CVE-2018-13096

## Summary
Severity: Medium
Advisory: CVE-2018-13096
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13096
Type: osv

## Details
An issue was discovered in fs/f2fs/super.c in the Linux kernel through 4.14. A denial of service (out-of-bounds memory access and BUG) can occur upon encountering an abnormal bitmap size when mounting a crafted f2fs image.

## References
- https://usn.ubuntu.com/3821-1/
- http://packetstormsecurity.com/files/151420/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://usn.ubuntu.com/3821-2/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2018-10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://bugzilla.kernel.org/show_bug.cgi?id=200167
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=e34438c903b653daca2b2a7de95aed46226f8ed3
- https://seclists.org/bugtraq/2019/Jan/52
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e34438c903b653daca2b2a7de95aed46226f8ed3
