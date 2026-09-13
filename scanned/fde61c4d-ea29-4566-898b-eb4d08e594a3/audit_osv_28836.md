# [H] nsh: Restore skb->{protocol,data,mac_header} for outer header in nsh_gso_segment().

## Summary
Severity: High
Advisory: CVE-2024-36933
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36933
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nsh: Restore skb->{protocol,data,mac_header} for outer header in nsh_gso_segment().

syzbot triggered various splats (see [0] and links) by a crafted GSO
packet of VIRTIO_NET_HDR_GSO_UDP layering the following protocols:

  ETH_P_8021AD + ETH_P_NSH + ETH_P_IPV6 + IPPROTO_UDP

NSH can encapsulate IPv4, IPv6, Ethernet, NSH, and MPLS.  As the inner
protocol can be Ethernet, NSH GSO handler, nsh_gso_segment(), calls
skb_mac_gso_segment() to invoke inner protocol GSO handlers.

nsh_gso_segment() does the following for the original skb before
calling skb_mac_gso_segment()

  1. reset skb->network_header
  2. save the original skb->{mac_heaeder,mac_len} in a local variable
  3. pull the NSH header
  4. resets skb->mac_header
  5. set up skb->mac_len and skb->protocol for the inner protocol.

and does the following for the segmented skb

  6. set ntohs(ETH_P_NSH) to skb->protocol
  7. push the NSH header
  8. restore skb->mac_header
  9. set skb->mac_header + mac_len to skb->network_header
 10. restore skb->mac_len

There are two problems in 6-7 and 8-9.

  (a)
  After 6 & 7, skb->data points to the NSH header, so the outer header
  (ETH_P_8021AD in this case) is stripped when skb is sent out of netdev.

  Also, if NSH is encapsulated by NSH + Ethernet (so NSH-Ethernet-NSH),
  skb_pull() in the first nsh_gso_segment() will make skb->data point
  to the middle of the outer NSH or Ethernet header because the Ethernet
  header is not pulled by the second nsh_gso_segment().

  (b)
  While restoring skb->{mac_header,network_header} in 8 & 9,
  nsh_gso_segment() does not assume that the data in the linear
  buffer is shifted.

  However, udp6_ufo_fragment() could shift the data and change
  skb->mac_header accordingly as demonstrated by syzbot.

  If this happens, even the restored skb->mac_header points to
  the middle of the outer header.

It seems nsh_gso_segment() has never worked with outer headers so far.

At the end of nsh_gso_segment(), the outer header must be restored for
the segmented skb, instead of the NSH header.

To do that, let's calculate the outer header position relatively from
the inner header and set skb->{data,mac_header,protocol} properly.

[0]:
BUG: KMSAN: uninit-value in ipvlan_process_outbound drivers/net/ipvlan/ipvlan_core.c:524 [inline]
BUG: KMSAN: uninit-value in ipvlan_xmit_mode_l3 drivers/net/ipvlan/ipvlan_core.c:602 [inline]
BUG: KMSAN: uninit-value in ipvlan_queue_xmit+0xf44/0x16b0 drivers/net/ipvlan/ipvlan_core.c:668
 ipvlan_process_outbound drivers/net/ipvlan/ipvlan_core.c:524 [inline]
 ipvlan_xmit_mode_l3 drivers/net/ipvlan/ipvlan_core.c:602 [inline]
 ipvlan_queue_xmit+0xf44/0x16b0 drivers/net/ipvlan/ipvlan_core.c:668
 ipvlan_start_xmit+0x5c/0x1a0 drivers/net/ipvlan/ipvlan_main.c:222
 __netdev_start_xmit include/linux/netdevice.h:4989 [inline]
 netdev_start_xmit include/linux/netdevice.h:5003 [inline]
 xmit_one net/core/dev.c:3547 [inline]
 dev_hard_start_xmit+0x244/0xa10 net/core/dev.c:3563
 __dev_queue_xmit+0x33ed/0x51c0 net/core/dev.c:4351
 dev_queue_xmit include/linux/netdevice.h:3171 [inline]
 packet_xmit+0x9c/0x6b0 net/packet/af_packet.c:276
 packet_snd net/packet/af_packet.c:3081 [inline]
 packet_sendmsg+0x8aef/0x9f10 net/packet/af_packet.c:3113
 sock_sendmsg_nosec net/socket.c:730 [inline]
 __sock_sendmsg net/socket.c:745 [inline]
 __sys_sendto+0x735/0xa10 net/socket.c:2191
 __do_sys_sendto net/socket.c:2203 [inline]
 __se_sys_sendto net/socket.c:2199 [inline]
 __x64_sys_sendto+0x125/0x1c0 net/socket.c:2199
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

Uninit was created at:
 slab_post_alloc_hook mm/slub.c:3819 [inline]
 slab_alloc_node mm/slub.c:3860 [inline]
 __do_kmalloc_node mm/slub.c:3980 [inline]
 __kmalloc_node_track_caller+0x705/0x1000 mm/slub.c:4001
 kmalloc_reserve+0x249/0x4a0 net/core/skbuff.c:582
 __
---truncated---

## References
- https://git.kernel.org/stable/c/29a07f2ee4d273760c2acbfc756e29eccd82470a
- https://git.kernel.org/stable/c/37ed6f244ec5bda2e90b085084e322ea55d0aaa2
- https://git.kernel.org/stable/c/46134031c20fd313d03b90169d64b2e05ca6b65c
- https://git.kernel.org/stable/c/4b911a9690d72641879ea6d13cce1de31d346d79
- https://git.kernel.org/stable/c/5a4603fbc285752d19e4b415466db18ef3617e4a
- https://git.kernel.org/stable/c/696d18bb59727a2e0526c0802a812620be1c9340
- https://git.kernel.org/stable/c/a7c2c3c1caabcb4a3d6c47284c397507aaf54fe9
- https://git.kernel.org/stable/c/bbccf0caef2fa917d6d0692385a06ce3c262a216
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36933.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36933
- https://security.netapp.com/advisory/ntap-20240912-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
