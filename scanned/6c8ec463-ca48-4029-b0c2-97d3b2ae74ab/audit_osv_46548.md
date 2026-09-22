# [M] CVE-2013-2128

## Summary
Severity: Medium
Advisory: CVE-2013-2128
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2013-06-07
Source: https://osv.dev/vulnerability/CVE-2013-2128
Type: osv

## Details
The tcp_read_sock function in net/ipv4/tcp.c in the Linux kernel before 2.6.34 does not properly manage skb consumption, which allows local users to cause a denial of service (system crash) via a crafted splice system call for a TCP socket.

## References
- http://rhn.redhat.com/errata/RHSA-2013-1051.html
- http://www.openwall.com/lists/oss-security/2013/05/29/11
- https://bugzilla.redhat.com/show_bug.cgi?id=968484
- https://github.com/torvalds/linux/commit/baff42ab1494528907bf4d5870359e31711746ae
- http://www.openwall.com/lists/oss-security/2013/05/29/11
- http://www.openwall.com/lists/oss-security/2013/05/29/11
- https://bugzilla.redhat.com/show_bug.cgi?id=968484
- https://github.com/torvalds/linux/commit/baff42ab1494528907bf4d5870359e31711746ae
- https://bugzilla.redhat.com/show_bug.cgi?id=968484
- http://ftp.osuosl.org/pub/linux/kernel/v2.6/ChangeLog-2.6.34
- http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git%3Ba=commit%3Bh=baff42ab1494528907bf4d5870359e31711746ae
