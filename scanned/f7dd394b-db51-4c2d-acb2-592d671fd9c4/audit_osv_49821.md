# [M] CVE-2019-19524

## Summary
Severity: Medium
Advisory: CVE-2019-19524
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19524
Type: osv

## Details
In the Linux kernel before 5.3.12, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/input/ff-memless.c driver, aka CID-fa3a5a1880c9.

## References
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4226-1/
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4227-2/
- https://usn.ubuntu.com/4228-1/
- https://usn.ubuntu.com/4227-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.12
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4225-2/
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://usn.ubuntu.com/4228-2/
- https://seclists.org/bugtraq/2020/Jan/10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fa3a5a1880c91bb92594ad42dfe9eedad7996b86
