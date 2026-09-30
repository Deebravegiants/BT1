# [H] net: ip_tunnel: make sure to pull inner header in ip_tunnel_rcv()

## Summary
Severity: High
Advisory: CVE-2024-26882
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26882
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ip_tunnel: make sure to pull inner header in ip_tunnel_rcv()

Apply the same fix than ones found in :

8d975c15c0cd ("ip6_tunnel: make sure to pull inner header in __ip6_tnl_rcv()")
1ca1ba465e55 ("geneve: make sure to pull inner header in geneve_rx()")

We have to save skb->network_header in a temporary variable
in order to be able to recompute the network_header pointer
after a pskb_inet_may_pull() call.

pskb_inet_may_pull() makes sure the needed headers are in skb->head.

syzbot reported:
BUG: KMSAN: uninit-value in __INET_ECN_decapsulate include/net/inet_ecn.h:253 [inline]
 BUG: KMSAN: uninit-value in INET_ECN_decapsulate include/net/inet_ecn.h:275 [inline]
 BUG: KMSAN: uninit-value in IP_ECN_decapsulate include/net/inet_ecn.h:302 [inline]
 BUG: KMSAN: uninit-value in ip_tunnel_rcv+0xed9/0x2ed0 net/ipv4/ip_tunnel.c:409
  __INET_ECN_decapsulate include/net/inet_ecn.h:253 [inline]
  INET_ECN_decapsulate include/net/inet_ecn.h:275 [inline]
  IP_ECN_decapsulate include/net/inet_ecn.h:302 [inline]
  ip_tunnel_rcv+0xed9/0x2ed0 net/ipv4/ip_tunnel.c:409
  __ipgre_rcv+0x9bc/0xbc0 net/ipv4/ip_gre.c:389
  ipgre_rcv net/ipv4/ip_gre.c:411 [inline]
  gre_rcv+0x423/0x19f0 net/ipv4/ip_gre.c:447
  gre_rcv+0x2a4/0x390 net/ipv4/gre_demux.c:163
  ip_protocol_deliver_rcu+0x264/0x1300 net/ipv4/ip_input.c:205
  ip_local_deliver_finish+0x2b8/0x440 net/ipv4/ip_input.c:233
  NF_HOOK include/linux/netfilter.h:314 [inline]
  ip_local_deliver+0x21f/0x490 net/ipv4/ip_input.c:254
  dst_input include/net/dst.h:461 [inline]
  ip_rcv_finish net/ipv4/ip_input.c:449 [inline]
  NF_HOOK include/linux/netfilter.h:314 [inline]
  ip_rcv+0x46f/0x760 net/ipv4/ip_input.c:569
  __netif_receive_skb_one_core net/core/dev.c:5534 [inline]
  __netif_receive_skb+0x1a6/0x5a0 net/core/dev.c:5648
  netif_receive_skb_internal net/core/dev.c:5734 [inline]
  netif_receive_skb+0x58/0x660 net/core/dev.c:5793
  tun_rx_batched+0x3ee/0x980 drivers/net/tun.c:1556
  tun_get_user+0x53b9/0x66e0 drivers/net/tun.c:2009
  tun_chr_write_iter+0x3af/0x5d0 drivers/net/tun.c:2055
  call_write_iter include/linux/fs.h:2087 [inline]
  new_sync_write fs/read_write.c:497 [inline]
  vfs_write+0xb6b/0x1520 fs/read_write.c:590
  ksys_write+0x20f/0x4c0 fs/read_write.c:643
  __do_sys_write fs/read_write.c:655 [inline]
  __se_sys_write fs/read_write.c:652 [inline]
  __x64_sys_write+0x93/0xd0 fs/read_write.c:652
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

Uninit was created at:
  __alloc_pages+0x9a6/0xe00 mm/page_alloc.c:4590
  alloc_pages_mpol+0x62b/0x9d0 mm/mempolicy.c:2133
  alloc_pages+0x1be/0x1e0 mm/mempolicy.c:2204
  skb_page_frag_refill+0x2bf/0x7c0 net/core/sock.c:2909
  tun_build_skb drivers/net/tun.c:1686 [inline]
  tun_get_user+0xe0a/0x66e0 drivers/net/tun.c:1826
  tun_chr_write_iter+0x3af/0x5d0 drivers/net/tun.c:2055
  call_write_iter include/linux/fs.h:2087 [inline]
  new_sync_write fs/read_write.c:497 [inline]
  vfs_write+0xb6b/0x1520 fs/read_write.c:590
  ksys_write+0x20f/0x4c0 fs/read_write.c:643
  __do_sys_write fs/read_write.c:655 [inline]
  __se_sys_write fs/read_write.c:652 [inline]
  __x64_sys_write+0x93/0xd0 fs/read_write.c:652
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/5c03387021cfa3336b97e0dcba38029917a8af2a
- https://git.kernel.org/stable/c/60044ab84836359534bd7153b92e9c1584140e4a
- https://git.kernel.org/stable/c/77fd5294ea09b21f6772ac954a121b87323cec80
- https://git.kernel.org/stable/c/b0ec2abf98267f14d032102551581c833b0659d3
- https://git.kernel.org/stable/c/c4c857723b37c20651300b3de4ff25059848b4b0
- https://git.kernel.org/stable/c/ca914f1cdee8a85799942c9b0ce5015bbd6844e1
- https://git.kernel.org/stable/c/ec6bb01e02cbd47781dd90775b631a1dc4bd9d2b
- https://git.kernel.org/stable/c/f6723d8dbfdc10c784a56748f86a9a3cd410dbd5
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26882.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26882
- https://security.netapp.com/advisory/ntap-20241220-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
