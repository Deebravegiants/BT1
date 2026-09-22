# [H] net: tls: explicitly disallow disconnect

## Summary
Severity: High
Advisory: CVE-2025-37756
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37756
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: explicitly disallow disconnect

syzbot discovered that it can disconnect a TLS socket and then
run into all sort of unexpected corner cases. I have a vague
recollection of Eric pointing this out to us a long time ago.
Supporting disconnect is really hard, for one thing if offload
is enabled we'd need to wait for all packets to be _acked_.
Disconnect is not commonly used, disallow it.

The immediate problem syzbot run into is the warning in the strp,
but that's just the easiest bug to trigger:

  WARNING: CPU: 0 PID: 5834 at net/tls/tls_strp.c:486 tls_strp_msg_load+0x72e/0xa80 net/tls/tls_strp.c:486
  RIP: 0010:tls_strp_msg_load+0x72e/0xa80 net/tls/tls_strp.c:486
  Call Trace:
   <TASK>
   tls_rx_rec_wait+0x280/0xa60 net/tls/tls_sw.c:1363
   tls_sw_recvmsg+0x85c/0x1c30 net/tls/tls_sw.c:2043
   inet6_recvmsg+0x2c9/0x730 net/ipv6/af_inet6.c:678
   sock_recvmsg_nosec net/socket.c:1023 [inline]
   sock_recvmsg+0x109/0x280 net/socket.c:1045
   __sys_recvfrom+0x202/0x380 net/socket.c:2237

## References
- http://www.openwall.com/lists/oss-security/2026/05/07/1
- https://git.kernel.org/stable/c/2bcad8fefcecdd5f005d8c550b25d703c063c34a
- https://git.kernel.org/stable/c/5071a1e606b30c0c11278d3c6620cd6a24724cf6
- https://git.kernel.org/stable/c/7bdcf5bc35ae59fc4a0fa23276e84b4d1534a3cf
- https://git.kernel.org/stable/c/8513411ec321942bd3cfed53d5bb700665c67d86
- https://git.kernel.org/stable/c/9fcbca0f801580cbb583e9cb274e2c7fbe766ca6
- https://git.kernel.org/stable/c/ac91c6125468be720eafde9c973994cb45b61d44
- https://git.kernel.org/stable/c/c665bef891e8972e1d3ce5bbc0d42a373346a2c3
- https://git.kernel.org/stable/c/f3ce4d3f874ab7919edca364c147ac735f9f1d04
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37756.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37756
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
