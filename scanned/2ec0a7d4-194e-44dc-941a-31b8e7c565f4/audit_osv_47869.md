# [M] CVE-2017-14106

## Summary
Severity: Medium
Advisory: CVE-2017-14106
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-14106
Type: osv

## Details
The tcp_disconnect function in net/ipv4/tcp.c in the Linux kernel before 4.12 allows local users to cause a denial of service (__tcp_select_window divide-by-zero error and system crash) by triggering a disconnect within a certain tcp_recvmsg code path.

## References
- http://www.securityfocus.com/bid/100878
- https://www.mail-archive.com/netdev%40vger.kernel.org/msg186255.html
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://www.securitytracker.com/id/1039549
- https://access.redhat.com/errata/RHSA-2017:2918
- https://access.redhat.com/errata/RHSA-2017:2931
- https://access.redhat.com/errata/RHSA-2017:3200
- https://access.redhat.com/errata/RHSA-2018:2172
- http://www.debian.org/security/2017/dsa-3981
- https://access.redhat.com/errata/RHSA-2017:2930
- https://github.com/torvalds/linux/commit/499350a5a6e7512d9ed369ed63a4244b6536f4f8
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=499350a5a6e7512d9ed369ed63a4244b6536f4f8
