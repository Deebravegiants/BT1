# [M] CVE-2016-0723

## Summary
Severity: Medium
Advisory: CVE-2016-0723
CVSS: 6.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2016-0723
Type: osv

## Details
Race condition in the tty_ioctl function in drivers/tty/tty_io.c in the Linux kernel through 4.4.1 allows local users to obtain sensitive information from kernel memory or cause a denial of service (use-after-free and system crash) by making a TIOCGETD ioctl call during processing of a TIOCSETD ioctl call.

## References
- http://www.securitytracker.com/id/1035695
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.securityfocus.com/bid/82950
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- https://security-tracker.debian.org/tracker/CVE-2016-0723
- https://support.f5.com/csp/article/K43650115
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176464.html
- http://source.android.com/security/bulletin/2016-07-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5c17c861a357e9458001f021a7afa7aab9937439
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2948-2
- http://www.debian.org/security/2016/dsa-3448
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2929-1
