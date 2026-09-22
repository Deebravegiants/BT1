# [M] CVE-2014-7970

## Summary
Severity: Medium
Advisory: CVE-2014-7970
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-10-13
Source: https://osv.dev/vulnerability/CVE-2014-7970
Type: osv

## Details
The pivot_root implementation in fs/namespace.c in the Linux kernel through 3.17 does not properly interact with certain locations of a chroot directory, which allows local users to cause a denial of service (mount-tree loop) via . (dot) values in both arguments to the pivot_root system call.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://secunia.com/advisories/60174
- http://secunia.com/advisories/61142
- http://www.openwall.com/lists/oss-security/2014/10/08/21
- http://www.securityfocus.com/bid/70319
- http://www.securitytracker.com/id/1030991
- http://www.spinics.net/lists/linux-fsdevel/msg79153.html
- http://www.ubuntu.com/usn/USN-2419-1
- http://www.ubuntu.com/usn/USN-2420-1
- http://www.ubuntu.com/usn/USN-2513-1
- http://www.ubuntu.com/usn/USN-2514-1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://bugzilla.redhat.com/show_bug.cgi?id=1151095
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96921
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0d0826019e529f21c84687521d03f60cd241ca7d
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://www.openwall.com/lists/oss-security/2014/10/08/21
- http://www.spinics.net/lists/linux-fsdevel/msg79153.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0d0826019e529f21c84687521d03f60cd241ca7d
