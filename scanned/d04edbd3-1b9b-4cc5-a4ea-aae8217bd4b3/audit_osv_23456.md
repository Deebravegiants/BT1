# [H] can: isotp: fix potential CAN frame reception race in isotp_rcv()

## Summary
Severity: High
Advisory: CVE-2022-48830
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48830
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.101, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: fix potential CAN frame reception race in isotp_rcv()

When receiving a CAN frame the current code logic does not consider
concurrently receiving processes which do not show up in real world
usage.

Ziyang Xuan writes:

The following syz problem is one of the scenarios. so->rx.len is
changed by isotp_rcv_ff() during isotp_rcv_cf(), so->rx.len equals
0 before alloc_skb() and equals 4096 after alloc_skb(). That will
trigger skb_over_panic() in skb_put().

=======================================================
CPU: 1 PID: 19 Comm: ksoftirqd/1 Not tainted 5.16.0-rc8-syzkaller #0
RIP: 0010:skb_panic+0x16c/0x16e net/core/skbuff.c:113
Call Trace:
 <TASK>
 skb_over_panic net/core/skbuff.c:118 [inline]
 skb_put.cold+0x24/0x24 net/core/skbuff.c:1990
 isotp_rcv_cf net/can/isotp.c:570 [inline]
 isotp_rcv+0xa38/0x1e30 net/can/isotp.c:668
 deliver net/can/af_can.c:574 [inline]
 can_rcv_filter+0x445/0x8d0 net/can/af_can.c:635
 can_receive+0x31d/0x580 net/can/af_can.c:665
 can_rcv+0x120/0x1c0 net/can/af_can.c:696
 __netif_receive_skb_one_core+0x114/0x180 net/core/dev.c:5465
 __netif_receive_skb+0x24/0x1b0 net/core/dev.c:5579

Therefore we make sure the state changes and data structures stay
consistent at CAN frame reception time by adding a spin_lock in
isotp_rcv(). This fixes the issue reported by syzkaller but does not
affect real world operation.

## References
- https://git.kernel.org/stable/c/5b068f33bc8acfcfd5ea7992a2dafb30d89bad30
- https://git.kernel.org/stable/c/7b53d2204ce79b27a878074a77d64f40ec21dbca
- https://git.kernel.org/stable/c/7c759040c1dd03954f650f147ae7175476d51314
- https://git.kernel.org/stable/c/f90cc68f9f4b5d8585ad5d0a206a9d37ac299ef3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48830.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
