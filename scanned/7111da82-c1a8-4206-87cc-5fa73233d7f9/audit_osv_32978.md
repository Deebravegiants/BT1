# [C] tls: always refresh the queue when reading sock

## Summary
Severity: Critical
Advisory: CVE-2025-38471
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38471
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: always refresh the queue when reading sock

After recent changes in net-next TCP compacts skbs much more
aggressively. This unearthed a bug in TLS where we may try
to operate on an old skb when checking if all skbs in the
queue have matching decrypt state and geometry.

    BUG: KASAN: slab-use-after-free in tls_strp_check_rcv+0x898/0x9a0 [tls]
    (net/tls/tls_strp.c:436 net/tls/tls_strp.c:530 net/tls/tls_strp.c:544)
    Read of size 4 at addr ffff888013085750 by task tls/13529

    CPU: 2 UID: 0 PID: 13529 Comm: tls Not tainted 6.16.0-rc5-virtme
    Call Trace:
     kasan_report+0xca/0x100
     tls_strp_check_rcv+0x898/0x9a0 [tls]
     tls_rx_rec_wait+0x2c9/0x8d0 [tls]
     tls_sw_recvmsg+0x40f/0x1aa0 [tls]
     inet_recvmsg+0x1c3/0x1f0

Always reload the queue, fast path is to have the record in the queue
when we wake, anyway (IOW the path going down "if !strp->stm.full_len").

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1f3a429c21e0e43e8b8c55d30701e91411a4df02
- https://git.kernel.org/stable/c/4ab26bce3969f8fd925fe6f6f551e4d1a508c68b
- https://git.kernel.org/stable/c/730fed2ff5e259495712518e18d9f521f61972bb
- https://git.kernel.org/stable/c/c76f6f437c46b2390888e0e1dc7aafafa9f4e0c6
- https://git.kernel.org/stable/c/cdb767915fc9a15d88d19d52a1455f1dc3e5ddc8
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38471.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
