# [M] CVE-2016-2548

## Summary
Severity: Medium
Advisory: CVE-2016-2548
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2548
Type: osv

## Details
sound/core/timer.c in the Linux kernel before 4.4.1 retains certain linked lists after a close or stop action, which allows local users to cause a denial of service (system crash) via a crafted ioctl call, related to the (1) snd_timer_close and (2) _snd_timer_stop functions.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.openwall.com/lists/oss-security/2016/01/19/1
- http://www.securityfocus.com/bid/83383
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securitytracker.com/id/1035306
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2931-1
- http://www.ubuntu.com/usn/USN-2932-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b5a663aa426f4884c71cd8580adae73f33570f0d
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2930-3
- https://bugzilla.redhat.com/show_bug.cgi?id=1311568
- https://github.com/torvalds/linux/commit/b5a663aa426f4884c71cd8580adae73f33570f0d
