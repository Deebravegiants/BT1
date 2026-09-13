# [H] CVE-2016-10200

## Summary
Severity: High
Advisory: CVE-2016-10200
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2016-10200
Type: osv

## Details
Race condition in the L2TPv3 IP Encapsulation feature in the Linux kernel before 4.8.14 allows local users to gain privileges or cause a denial of service (use-after-free) by making multiple bind system calls without properly ascertaining whether a socket has the SOCK_ZAPPED status, related to net/l2tp/l2tp_ip.c and net/l2tp/l2tp_ip6.c.

## References
- http://www.securityfocus.com/bid/101783
- https://access.redhat.com/errata/RHSA-2017:1842
- http://source.android.com/security/bulletin/2017-03-01.html
- http://www.securitytracker.com/id/1037965
- http://www.securitytracker.com/id/1037968
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2437
- https://access.redhat.com/errata/RHSA-2017:2444
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.14
- https://github.com/torvalds/linux/commit/32c231164b762dddefa13af5a0101032c70b50ef
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=32c231164b762dddefa13af5a0101032c70b50ef
