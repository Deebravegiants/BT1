# [H] CVE-2016-1583

## Summary
Severity: High
Advisory: CVE-2016-1583
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-1583
Type: osv

## Details
The ecryptfs_privileged_open function in fs/ecryptfs/kthread.c in the Linux kernel before 4.6.3 allows local users to gain privileges or cause a denial of service (stack memory consumption) via vectors involving crafted mmap calls for /proc pathnames, leading to recursive pagefault handling.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-3006-1
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.3
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://packetstormsecurity.com/files/137560/Linux-ecryptfs-Stack-Overflow.html
- https://access.redhat.com/errata/RHSA-2017:2760
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00016.html
- http://www.openwall.com/lists/oss-security/2016/06/10/8
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-2999-1
- http://www.ubuntu.com/usn/USN-3000-1
