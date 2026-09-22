# [H] ip6_tunnel: make sure to pull inner header in __ip6_tnl_rcv()

## Summary
Severity: High
Advisory: CVE-2024-26641
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-26641
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_tunnel: make sure to pull inner header in __ip6_tnl_rcv()

syzbot found __ip6_tnl_rcv() could access unitiliazed data [1].

Call pskb_inet_may_pull() to fix this, and initialize ipv6h
variable after this call as it can change skb->head.

[1]
 BUG: KMSAN: uninit-value in __INET_ECN_decapsulate include/net/inet_ecn.h:253 [inline]
 BUG: KMSAN: uninit-value in INET_ECN_decapsulate include/net/inet_ecn.h:275 [inline]
 BUG: KMSAN: uninit-value in IP6_ECN_decapsulate+0x7df/0x1e50 include/net/inet_ecn.h:321
  __INET_ECN_decapsulate include/net/inet_ecn.h:253 [inline]
  INET_ECN_decapsulate include/net/inet_ecn.h:275 [inline]
  IP6_ECN_decapsulate+0x7df/0x1e50 include/net/inet_ecn.h:321
  ip6ip6_dscp_ecn_decapsulate+0x178/0x1b0 net/ipv6/ip6_tunnel.c:727
  __ip6_tnl_rcv+0xd4e/0x1590 net/ipv6/ip6_tunnel.c:845
  ip6_tnl_rcv+0xce/0x100 net/ipv6/ip6_tunnel.c:888
 gre_rcv+0x143f/0x1870
  ip6_protocol_deliver_rcu+0xda6/0x2a60 net/ipv6/ip6_input.c:438
  ip6_input_finish net/ipv6/ip6_input.c:483 [inline]
  NF_HOOK include/linux/netfilter.h:314 [inline]
  ip6_input+0x15d/0x430 net/ipv6/ip6_input.c:492
  ip6_mc_input+0xa7e/0xc80 net/ipv6/ip6_input.c:586
  dst_input include/net/dst.h:461 [inline]
  ip6_rcv_finish+0x5db/0x870 net/ipv6/ip6_input.c:79
  NF_HOOK include/linux/netfilter.h:314 [inline]
  ipv6_rcv+0xda/0x390 net/ipv6/ip6_input.c:310
  __netif_receive_skb_one_core net/core/dev.c:5532 [inline]
  __netif_receive_skb+0x1a6/0x5a0 net/core/dev.c:5646
  netif_receive_skb_internal net/core/dev.c:5732 [inline]
  netif_receive_skb+0x58/0x660 net/core/dev.c:5791
  tun_rx_batched+0x3ee/0x980 drivers/net/tun.c:1555
  tun_get_user+0x53af/0x66d0 drivers/net/tun.c:2002
  tun_chr_write_iter+0x3af/0x5d0 drivers/net/tun.c:2048
  call_write_iter include/linux/fs.h:2084 [inline]
  new_sync_write fs/read_write.c:497 [inline]
  vfs_write+0x786/0x1200 fs/read_write.c:590
  ksys_write+0x20f/0x4c0 fs/read_write.c:643
  __do_sys_write fs/read_write.c:655 [inline]
  __se_sys_write fs/read_write.c:652 [inline]
  __x64_sys_write+0x93/0xd0 fs/read_write.c:652
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0x6d/0x140 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

Uninit was created at:
  slab_post_alloc_hook+0x129/0xa70 mm/slab.h:768
  slab_alloc_node mm/slub.c:3478 [inline]
  kmem_cache_alloc_node+0x5e9/0xb10 mm/slub.c:3523
  kmalloc_reserve+0x13d/0x4a0 net/core/skbuff.c:560
  __alloc_skb+0x318/0x740 net/core/skbuff.c:651
  alloc_skb include/linux/skbuff.h:1286 [inline]
  alloc_skb_with_frags+0xc8/0xbd0 net/core/skbuff.c:6334
  sock_alloc_send_pskb+0xa80/0xbf0 net/core/sock.c:2787
  tun_alloc_skb drivers/net/tun.c:1531 [inline]
  tun_get_user+0x1e8a/0x66d0 drivers/net/tun.c:1846
  tun_chr_write_iter+0x3af/0x5d0 drivers/net/tun.c:2048
  call_write_iter include/linux/fs.h:2084 [inline]
  new_sync_write fs/read_write.c:497 [inline]
  vfs_write+0x786/0x1200 fs/read_write.c:590
  ksys_write+0x20f/0x4c0 fs/read_write.c:643
  __do_sys_write fs/read_write.c:655 [inline]
  __se_sys_write fs/read_write.c:652 [inline]
  __x64_sys_write+0x93/0xd0 fs/read_write.c:652
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0x6d/0x140 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

CPU: 0 PID: 5034 Comm: syz-executor331 Not tainted 6.7.0-syzkaller-00562-g9f8413c4a66f #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 11/17/2023

## References
- https://git.kernel.org/stable/c/350a6640fac4b53564ec20aa3f4a0922cb0ba5e6
- https://git.kernel.org/stable/c/8d975c15c0cd744000ca386247432d57b21f9df0
- https://git.kernel.org/stable/c/a9bc32879a08f23cdb80a48c738017e39aea1080
- https://git.kernel.org/stable/c/af6b5c50d47ab43e5272ad61935d0ed2e264d3f0
- https://git.kernel.org/stable/c/c835df3bcc14858ae9b27315dd7de76370b94f3a
- https://git.kernel.org/stable/c/d54e4da98bbfa8c257bdca94c49652d81d18a4d8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26641.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26641
- https://security.netapp.com/advisory/ntap-20241108-0008/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
