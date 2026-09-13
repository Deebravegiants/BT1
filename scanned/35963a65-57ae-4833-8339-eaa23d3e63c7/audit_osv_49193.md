# [M] CVE-2018-5333

## Summary
Severity: Medium
Advisory: CVE-2018-5333
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/CVE-2018-5333
Type: osv

## Details
In the Linux kernel through 4.14.13, the rds_cmsg_atomic function in net/rds/rdma.c mishandles cases where page pinning fails or an invalid address is supplied, leading to an rds_atomic_free_op NULL pointer dereference.

## References
- http://packetstormsecurity.com/files/156053/Reliable-Datagram-Sockets-RDS-rds_atomic_free_op-Privilege-Escalation.html
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-1/
- http://www.securityfocus.com/bid/102510
- https://usn.ubuntu.com/3617-3/
- https://access.redhat.com/errata/RHSA-2018:0470
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3619-2/
- https://www.debian.org/security/2018/dsa-4187
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3632-1/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7d11f77f84b27cef452cee332f4e469503084737
- https://github.com/torvalds/linux/commit/7d11f77f84b27cef452cee332f4e469503084737
