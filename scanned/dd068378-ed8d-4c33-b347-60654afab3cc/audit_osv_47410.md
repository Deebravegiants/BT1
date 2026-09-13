# [H] CVE-2016-4951

## Summary
Severity: High
Advisory: CVE-2016-4951
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4951
Type: osv

## Details
The tipc_nl_publ_dump function in net/tipc/socket.c in the Linux kernel through 4.6 does not verify socket existence, which allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via a dumpit operation.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=45e093ae2830cd1264677d47ff9a95a71f5d9f9c
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.ubuntu.com/usn/USN-3016-1
- http://www.ubuntu.com/usn/USN-3016-2
- http://www.ubuntu.com/usn/USN-3017-2
- http://www.ubuntu.com/usn/USN-3017-3
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.openwall.com/lists/oss-security/2016/05/21/2
- http://www.ubuntu.com/usn/USN-3016-3
- http://www.ubuntu.com/usn/USN-3020-1
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.ubuntu.com/usn/USN-3016-4
- https://github.com/torvalds/linux/commit/45e093ae2830cd1264677d47ff9a95a71f5d9f9c
- http://www.ubuntu.com/usn/USN-3017-1
- http://lists.openwall.net/netdev/2016/05/14/28
