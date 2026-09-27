# [H] af_packet: fix vlan_get_tci() vs MSG_PEEK

## Summary
Severity: High
Advisory: CVE-2024-57902
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57902
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_packet: fix vlan_get_tci() vs MSG_PEEK

Blamed commit forgot MSG_PEEK case, allowing a crash [1] as found
by syzbot.

Rework vlan_get_tci() to not touch skb at all,
so that it can be used from many cpus on the same skb.

Add a const qualifier to skb argument.

[1]
skbuff: skb_under_panic: text:ffffffff8a8da482 len:32 put:14 head:ffff88807a1d5800 data:ffff88807a1d5810 tail:0x14 end:0x140 dev:<NULL>
------------[ cut here ]------------
 kernel BUG at net/core/skbuff.c:206 !
Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI
CPU: 0 UID: 0 PID: 5880 Comm: syz-executor172 Not tainted 6.13.0-rc3-syzkaller-00762-g9268abe611b0 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
 RIP: 0010:skb_panic net/core/skbuff.c:206 [inline]
 RIP: 0010:skb_under_panic+0x14b/0x150 net/core/skbuff.c:216
Code: 0b 8d 48 c7 c6 9e 6c 26 8e 48 8b 54 24 08 8b 0c 24 44 8b 44 24 04 4d 89 e9 50 41 54 41 57 41 56 e8 3a 5a 79 f7 48 83 c4 20 90 <0f> 0b 0f 1f 00 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 f3
RSP: 0018:ffffc90003baf5b8 EFLAGS: 00010286
RAX: 0000000000000087 RBX: dffffc0000000000 RCX: 8565c1eec37aa000
RDX: 0000000000000000 RSI: 0000000080000000 RDI: 0000000000000000
RBP: ffff88802616fb50 R08: ffffffff817f0a4c R09: 1ffff92000775e50
R10: dffffc0000000000 R11: fffff52000775e51 R12: 0000000000000140
R13: ffff88807a1d5800 R14: ffff88807a1d5810 R15: 0000000000000014
FS:  00007fa03261f6c0(0000) GS:ffff8880b8600000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007ffd65753000 CR3: 0000000031720000 CR4: 00000000003526f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
  skb_push+0xe5/0x100 net/core/skbuff.c:2636
  vlan_get_tci+0x272/0x550 net/packet/af_packet.c:565
  packet_recvmsg+0x13c9/0x1ef0 net/packet/af_packet.c:3616
  sock_recvmsg_nosec net/socket.c:1044 [inline]
  sock_recvmsg+0x22f/0x280 net/socket.c:1066
  ____sys_recvmsg+0x1c6/0x480 net/socket.c:2814
  ___sys_recvmsg net/socket.c:2856 [inline]
  do_recvmmsg+0x426/0xab0 net/socket.c:2951
  __sys_recvmmsg net/socket.c:3025 [inline]
  __do_sys_recvmmsg net/socket.c:3048 [inline]
  __se_sys_recvmmsg net/socket.c:3041 [inline]
  __x64_sys_recvmmsg+0x199/0x250 net/socket.c:3041
  do_syscall_x64 arch/x86/entry/common.c:52 [inline]
  do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/65c67049e9ed481f6b52264b39618b8c6dfb1d3e
- https://git.kernel.org/stable/c/66ffb0cf2125dcf9e902eede4a43653a24fd9cb2
- https://git.kernel.org/stable/c/77ee7a6d16b6ec07b5c3ae2b6b60a24c1afbed09
- https://git.kernel.org/stable/c/7aa78d0d8546d8ce5a764add3f55d72e707c18f1
- https://git.kernel.org/stable/c/b65292a548d847099a4fe0fff53122a06e798e25
- https://git.kernel.org/stable/c/d91b4a9baa018a001d5c884e236c0cfd31f9f4a1
- https://git.kernel.org/stable/c/fa57f07ba0622c8692f40e1300adca59277b0044
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57902.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57902
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
