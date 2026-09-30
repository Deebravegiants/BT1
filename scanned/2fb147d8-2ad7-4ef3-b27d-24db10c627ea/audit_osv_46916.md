# [M] CVE-2015-7990

## Summary
Severity: Medium
Advisory: CVE-2015-7990
CVSS: 5.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2015-12-28
Source: https://osv.dev/vulnerability/CVE-2015-7990
Type: osv

## Details
Race condition in the rds_sendmsg function in net/rds/sendmsg.c in the Linux kernel before 4.3.3 allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact by using a socket that was not properly bound.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-6937.

## References
- http://www.debian.org/security/2015/dsa-3396
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.3
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.ubuntu.com/usn/USN-2886-1
- http://www.ubuntu.com/usn/USN-2887-1
- http://www.ubuntu.com/usn/USN-2887-2
- http://www.ubuntu.com/usn/USN-2888-1
- http://www.ubuntu.com/usn/USN-2889-1
- http://www.ubuntu.com/usn/USN-2889-2
- http://www.ubuntu.com/usn/USN-2890-1
- http://www.ubuntu.com/usn/USN-2890-2
- http://www.ubuntu.com/usn/USN-2890-3
- https://github.com/torvalds/linux/commit/8c7188b23474cca017b3ef354c4a58456f68303a
- https://bugzilla.redhat.com/show_bug.cgi?id=1276437
- https://bugzilla.suse.com/show_bug.cgi?id=952384
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8c7188b23474cca017b3ef354c4a58456f68303a
- http://lists.opensuse.org/opensuse-security-announce/2015-11/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00026.html
