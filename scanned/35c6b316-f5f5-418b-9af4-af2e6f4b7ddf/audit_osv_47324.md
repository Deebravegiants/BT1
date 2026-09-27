# [M] CVE-2016-2549

## Summary
Severity: Medium
Advisory: CVE-2016-2549
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2549
Type: osv

## Details
sound/core/hrtimer.c in the Linux kernel before 4.4.1 does not prevent recursive callback access, which allows local users to cause a denial of service (deadlock) via a crafted ioctl call.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/83382
- http://www.openwall.com/lists/oss-security/2016/01/19/1
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2932-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2ba1fe7a06d3624f9a7586d672b55f08f7c670f3
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2931-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1311570
- https://github.com/torvalds/linux/commit/2ba1fe7a06d3624f9a7586d672b55f08f7c670f3
