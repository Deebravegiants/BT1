# [H] CVE-2012-6704

## Summary
Severity: High
Advisory: CVE-2012-6704
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2012-6704
Type: osv

## Details
The sock_setsockopt function in net/core/sock.c in the Linux kernel before 3.5 mishandles negative values of sk_sndbuf and sk_rcvbuf, which allows local users to cause a denial of service (memory corruption and system crash) or possibly have unspecified other impact by leveraging the CAP_NET_ADMIN capability for a crafted setsockopt system call with the (1) SO_SNDBUF or (2) SO_RCVBUF option.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=82981930125abfd39d7c8378a9cfdf5e1be2002b
- http://www.openwall.com/lists/oss-security/2016/12/03/1
- http://www.securityfocus.com/bid/95135
- https://bugzilla.redhat.com/show_bug.cgi?id=1402024
- https://github.com/torvalds/linux/commit/82981930125abfd39d7c8378a9cfdf5e1be2002b
- http://www.openwall.com/lists/oss-security/2016/12/03/1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=82981930125abfd39d7c8378a9cfdf5e1be2002b
- https://github.com/torvalds/linux/commit/82981930125abfd39d7c8378a9cfdf5e1be2002b
- https://bugzilla.redhat.com/show_bug.cgi?id=1402024
