# [H] CVE-2017-6214

## Summary
Severity: High
Advisory: CVE-2017-6214
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-23
Source: https://osv.dev/vulnerability/CVE-2017-6214
Type: osv

## Details
The tcp_splice_read function in net/ipv4/tcp.c in the Linux kernel before 4.9.11 allows remote attackers to cause a denial of service (infinite loop and soft lockup) via vectors involving a TCP packet with the URG flag.

## References
- http://www.securityfocus.com/bid/96421
- http://www.securitytracker.com/id/1037897
- https://source.android.com/security/bulletin/2017-09-01
- https://access.redhat.com/errata/RHSA-2017:1372
- https://access.redhat.com/errata/RHSA-2017:1647
- http://www.debian.org/security/2017/dsa-3804
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.11
- https://access.redhat.com/errata/RHSA-2017:1615
- https://access.redhat.com/errata/RHSA-2017:1616
- https://github.com/torvalds/linux/commit/ccf7abb93af09ad0868ae9033d1ca8108bdaec82
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ccf7abb93af09ad0868ae9033d1ca8108bdaec82
