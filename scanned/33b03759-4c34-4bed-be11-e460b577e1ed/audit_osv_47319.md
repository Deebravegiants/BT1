# [M] CVE-2016-2544

## Summary
Severity: Medium
Advisory: CVE-2016-2544
CVSS: 5.1 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2544
Type: osv

## Details
Race condition in the queue_delete function in sound/core/seq/seq_queue.c in the Linux kernel before 4.4.1 allows local users to cause a denial of service (use-after-free and system crash) by making an ioctl call at a certain time.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://www.securityfocus.com/bid/83380
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securitytracker.com/id/1035305
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.openwall.com/lists/oss-security/2016/01/19/1
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2931-1
- http://www.ubuntu.com/usn/USN-2932-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1311558
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3567eb6af614dac436c4b16a8d426f9faed639b3
- https://github.com/torvalds/linux/commit/3567eb6af614dac436c4b16a8d426f9faed639b3
