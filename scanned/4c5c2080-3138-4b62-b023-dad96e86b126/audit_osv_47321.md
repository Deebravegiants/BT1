# [M] CVE-2016-2546

## Summary
Severity: Medium
Advisory: CVE-2016-2546
CVSS: 5.1 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2546
Type: osv

## Details
sound/core/timer.c in the Linux kernel before 4.4.1 uses an incorrect type of mutex, which allows local users to cause a denial of service (race condition, use-after-free, and system crash) via a crafted ioctl call.

## References
- http://www.securitytracker.com/id/1035301
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/83384
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2931-1
- http://www.ubuntu.com/usn/USN-2932-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1311564
- https://github.com/torvalds/linux/commit/af368027a49a751d6ff4ee9e3f9961f35bb4fede
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=af368027a49a751d6ff4ee9e3f9961f35bb4fede
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.openwall.com/lists/oss-security/2016/01/19/1
