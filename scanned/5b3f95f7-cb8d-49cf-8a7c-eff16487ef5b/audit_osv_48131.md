# [H] CVE-2017-18509

## Summary
Severity: High
Advisory: CVE-2017-18509
Aliases: A-172999675, ASB-A-172999675
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2017-18509
Type: osv

## Details
An issue was discovered in net/ipv6/ip6mr.c in the Linux kernel before 4.11. By setting a specific socket option, an attacker can control a pointer in kernel land and cause an inet_csk_listen_stop general protection fault, or potentially execute arbitrary code under certain circumstances. The issue can be triggered as root (e.g., inside a default LXC container or with the CAP_NET_ADMIN capability) or after namespace unsharing. This occurs because sk_type and protocol are not checked in the appropriate part of the ip6_mroute_* functions. NOTE: this affects Linux distributions that use 4.9.x longterm kernels before 4.9.187.

## References
- https://support.f5.com/csp/article/K41582535?utm_source=f5support&amp%3Butm_medium=RSS
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://lists.openwall.net/netdev/2017/12/04/40
- https://usn.ubuntu.com/4145-1/
- https://salsa.debian.org/kernel-team/linux/commit/baefcdc2f29923e7325ce4e1a72c3ff0a9800f32
- https://seclists.org/bugtraq/2019/Aug/26
- https://support.f5.com/csp/article/K41582535
- https://www.debian.org/security/2019/dsa-4497
- https://github.com/torvalds/linux/commit/99253eb750fda6a644d5188fb26c43bad8d5a745
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=99253eb750fda6a644d5188fb26c43bad8d5a745
- https://pulsesecurity.co.nz/advisories/linux-kernel-4.9-inetcsklistenstop-gpf
