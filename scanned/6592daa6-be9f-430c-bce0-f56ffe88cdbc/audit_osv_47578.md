# [M] CVE-2016-8645

## Summary
Severity: Medium
Advisory: CVE-2016-8645
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-8645
Type: osv

## Details
The TCP stack in the Linux kernel before 4.8.10 mishandles skb truncation, which allows local users to cause a denial of service (system crash) via a crafted application that makes sendto system calls, related to net/ipv4/tcp_ipv4.c and net/ipv6/tcp_ipv6.c.

## References
- http://www.securitytracker.com/id/1037285
- http://www.openwall.com/lists/oss-security/2016/11/30/3
- http://www.securityfocus.com/bid/94264
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.10
- http://www.openwall.com/lists/oss-security/2016/11/11/3
- https://access.redhat.com/errata/RHSA-2017:2077
- https://bugzilla.redhat.com/show_bug.cgi?id=1393904
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ac6e780070e30e4c35bd395acfe9191e6268bdd3
- https://github.com/torvalds/linux/commit/ac6e780070e30e4c35bd395acfe9191e6268bdd3
