# [M] CVE-2021-47397

## Summary
Severity: Medium
Advisory: CVE-2021-47397
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47397
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: break out if skb_header_pointer returns NULL in sctp_rcv_ootb

We should always check if skb_header_pointer's return is NULL before
using it, otherwise it may cause null-ptr-deref, as syzbot reported:

  KASAN: null-ptr-deref in range [0x0000000000000000-0x0000000000000007]
  RIP: 0010:sctp_rcv_ootb net/sctp/input.c:705 [inline]
  RIP: 0010:sctp_rcv+0x1d84/0x3220 net/sctp/input.c:196
  Call Trace:
  <IRQ>
   sctp6_rcv+0x38/0x60 net/sctp/ipv6.c:1109
   ip6_protocol_deliver_rcu+0x2e9/0x1ca0 net/ipv6/ip6_input.c:422
   ip6_input_finish+0x62/0x170 net/ipv6/ip6_input.c:463
   NF_HOOK include/linux/netfilter.h:307 [inline]
   NF_HOOK include/linux/netfilter.h:301 [inline]
   ip6_input+0x9c/0xd0 net/ipv6/ip6_input.c:472
   dst_input include/net/dst.h:460 [inline]
   ip6_rcv_finish net/ipv6/ip6_input.c:76 [inline]
   NF_HOOK include/linux/netfilter.h:307 [inline]
   NF_HOOK include/linux/netfilter.h:301 [inline]
   ipv6_rcv+0x28c/0x3c0 net/ipv6/ip6_input.c:297

## References
- https://git.kernel.org/stable/c/77bc7dcf0fcc1519341a91788d7a2914fcfddf6d
- https://git.kernel.org/stable/c/8180611c238e11676612eb2a9828b1c7a3a4d77b
- https://git.kernel.org/stable/c/8c630a7b4f9dec63f08bd881ab77984a724a5124
- https://git.kernel.org/stable/c/9c6591ae8e63f93c895ad5e2703c36c548aac997
- https://git.kernel.org/stable/c/ec018021cf445abbe8e2f3e2a7f1dcc813cb8ea1
- https://git.kernel.org/stable/c/f7e745f8e94492a8ac0b0a26e25f2b19d342918f
