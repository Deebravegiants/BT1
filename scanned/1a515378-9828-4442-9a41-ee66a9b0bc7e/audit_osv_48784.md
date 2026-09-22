# [M] CVE-2018-13100

## Summary
Severity: Medium
Advisory: CVE-2018-13100
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13100
Type: osv

## Details
An issue was discovered in fs/f2fs/super.c in the Linux kernel through 4.17.3, which does not properly validate secs_per_zone in a corrupted f2fs image, as demonstrated by a divide-by-zero error.

## References
- https://usn.ubuntu.com/4118-1/
- http://packetstormsecurity.com/files/151420/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
- http://lists.opensuse.org/opensuse-security-announce/2018-10/msg00033.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=42bf546c1fe3f3654bdf914e977acbc2b80a5be5
- https://seclists.org/bugtraq/2019/Jan/52
- https://usn.ubuntu.com/4094-1/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- http://www.securityfocus.com/bid/104679
- https://bugzilla.kernel.org/show_bug.cgi?id=200183
