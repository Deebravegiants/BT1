# [C] slip: make slhc_remember() more robust against malicious packets

## Summary
Severity: Critical
Advisory: CVE-2024-50033
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50033
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

slip: make slhc_remember() more robust against malicious packets

syzbot found that slhc_remember() was missing checks against
malicious packets [1].

slhc_remember() only checked the size of the packet was at least 20,
which is not good enough.

We need to make sure the packet includes the IPv4 and TCP header
that are supposed to be carried.

Add iph and th pointers to make the code more readable.

[1]

BUG: KMSAN: uninit-value in slhc_remember+0x2e8/0x7b0 drivers/net/slip/slhc.c:666
  slhc_remember+0x2e8/0x7b0 drivers/net/slip/slhc.c:666
  ppp_receive_nonmp_frame+0xe45/0x35e0 drivers/net/ppp/ppp_generic.c:2455
  ppp_receive_frame drivers/net/ppp/ppp_generic.c:2372 [inline]
  ppp_do_recv+0x65f/0x40d0 drivers/net/ppp/ppp_generic.c:2212
  ppp_input+0x7dc/0xe60 drivers/net/ppp/ppp_generic.c:2327
  pppoe_rcv_core+0x1d3/0x720 drivers/net/ppp/pppoe.c:379
  sk_backlog_rcv+0x13b/0x420 include/net/sock.h:1113
  __release_sock+0x1da/0x330 net/core/sock.c:3072
  release_sock+0x6b/0x250 net/core/sock.c:3626
  pppoe_sendmsg+0x2b8/0xb90 drivers/net/ppp/pppoe.c:903
  sock_sendmsg_nosec net/socket.c:729 [inline]
  __sock_sendmsg+0x30f/0x380 net/socket.c:744
  ____sys_sendmsg+0x903/0xb60 net/socket.c:2602
  ___sys_sendmsg+0x28d/0x3c0 net/socket.c:2656
  __sys_sendmmsg+0x3c1/0x960 net/socket.c:2742
  __do_sys_sendmmsg net/socket.c:2771 [inline]
  __se_sys_sendmmsg net/socket.c:2768 [inline]
  __x64_sys_sendmmsg+0xbc/0x120 net/socket.c:2768
  x64_sys_call+0xb6e/0x3ba0 arch/x86/include/generated/asm/syscalls_64.h:308
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xcd/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Uninit was created at:
  slab_post_alloc_hook mm/slub.c:4091 [inline]
  slab_alloc_node mm/slub.c:4134 [inline]
  kmem_cache_alloc_node_noprof+0x6bf/0xb80 mm/slub.c:4186
  kmalloc_reserve+0x13d/0x4a0 net/core/skbuff.c:587
  __alloc_skb+0x363/0x7b0 net/core/skbuff.c:678
  alloc_skb include/linux/skbuff.h:1322 [inline]
  sock_wmalloc+0xfe/0x1a0 net/core/sock.c:2732
  pppoe_sendmsg+0x3a7/0xb90 drivers/net/ppp/pppoe.c:867
  sock_sendmsg_nosec net/socket.c:729 [inline]
  __sock_sendmsg+0x30f/0x380 net/socket.c:744
  ____sys_sendmsg+0x903/0xb60 net/socket.c:2602
  ___sys_sendmsg+0x28d/0x3c0 net/socket.c:2656
  __sys_sendmmsg+0x3c1/0x960 net/socket.c:2742
  __do_sys_sendmmsg net/socket.c:2771 [inline]
  __se_sys_sendmmsg net/socket.c:2768 [inline]
  __x64_sys_sendmmsg+0xbc/0x120 net/socket.c:2768
  x64_sys_call+0xb6e/0x3ba0 arch/x86/include/generated/asm/syscalls_64.h:308
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xcd/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

CPU: 0 UID: 0 PID: 5460 Comm: syz.2.33 Not tainted 6.12.0-rc2-syzkaller-00006-g87d6aab2389e #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/29e8d96d44f51cf89a62dd042be35d052833b95c
- https://git.kernel.org/stable/c/36b054324d18e51cf466134e13b6fbe3c91f52af
- https://git.kernel.org/stable/c/5e336384cc9b608e0551f99c3d87316ca3b0e51a
- https://git.kernel.org/stable/c/7d3fce8cbe3a70a1c7c06c9b53696be5d5d8dd5c
- https://git.kernel.org/stable/c/8bb79eb1db85a10865f0d4dd15b013def3f2d246
- https://git.kernel.org/stable/c/ba6501ea06462d6404d57d5644cf2854db38e7d7
- https://git.kernel.org/stable/c/ff5e0f895315706e4ca5a19df15be6866cee4f5d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50033.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50033
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
