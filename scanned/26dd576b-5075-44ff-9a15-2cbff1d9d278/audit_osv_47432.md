# [M] CVE-2016-5243

## Summary
Severity: Medium
Advisory: CVE-2016-5243
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-5243
Type: osv

## Details
The tipc_nl_compat_link_dump function in net/tipc/netlink_compat.c in the Linux kernel through 4.6.3 does not properly copy a certain string, which allows local users to obtain sensitive information from kernel stack memory by reading a Netlink message.

## References
- http://www.openwall.com/lists/oss-security/2016/06/03/4
- http://www.securityfocus.com/bid/91334
- http://www.ubuntu.com/usn/USN-3052-1
- http://www.ubuntu.com/usn/USN-3056-1
- http://www.ubuntu.com/usn/USN-3049-1
- http://www.ubuntu.com/usn/USN-3054-1
- https://github.com/torvalds/linux/commit/5d2be1422e02ccd697ccfcd45c85b4a26e6178e2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5d2be1422e02ccd697ccfcd45c85b4a26e6178e2
- http://www.ubuntu.com/usn/USN-3051-1
- http://www.ubuntu.com/usn/USN-3053-1
- http://www.ubuntu.com/usn/USN-3055-1
- http://www.ubuntu.com/usn/USN-3057-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3050-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1343335
- https://patchwork.ozlabs.org/patch/629100/
