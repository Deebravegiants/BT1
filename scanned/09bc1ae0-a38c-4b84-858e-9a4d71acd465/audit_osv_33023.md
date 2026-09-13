# [H] pptp: ensure minimal skb length in pptp_xmit()

## Summary
Severity: High
Advisory: CVE-2025-38574
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38574
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

pptp: ensure minimal skb length in pptp_xmit()

Commit aabc6596ffb3 ("net: ppp: Add bound checking for skb data
on ppp_sync_txmung") fixed ppp_sync_txmunge()

We need a similar fix in pptp_xmit(), otherwise we might
read uninit data as reported by syzbot.

BUG: KMSAN: uninit-value in pptp_xmit+0xc34/0x2720 drivers/net/ppp/pptp.c:193
  pptp_xmit+0xc34/0x2720 drivers/net/ppp/pptp.c:193
  ppp_channel_bridge_input drivers/net/ppp/ppp_generic.c:2290 [inline]
  ppp_input+0x1d6/0xe60 drivers/net/ppp/ppp_generic.c:2314
  pppoe_rcv_core+0x1e8/0x760 drivers/net/ppp/pppoe.c:379
  sk_backlog_rcv+0x142/0x420 include/net/sock.h:1148
  __release_sock+0x1d3/0x330 net/core/sock.c:3213
  release_sock+0x6b/0x270 net/core/sock.c:3767
  pppoe_sendmsg+0x15d/0xcb0 drivers/net/ppp/pppoe.c:904
  sock_sendmsg_nosec net/socket.c:712 [inline]
  __sock_sendmsg+0x330/0x3d0 net/socket.c:727
  ____sys_sendmsg+0x893/0xd80 net/socket.c:2566
  ___sys_sendmsg+0x271/0x3b0 net/socket.c:2620
  __sys_sendmmsg+0x2d9/0x7c0 net/socket.c:2709

## References
- https://git.kernel.org/stable/c/1a04db0fd75cb6034fc27a56b67b3b8b9022a98c
- https://git.kernel.org/stable/c/26672f1679b143aa34fca0b6046b7fd0c184770d
- https://git.kernel.org/stable/c/5005d24377378a20e5c0e53052fc4ebdcdcbc611
- https://git.kernel.org/stable/c/504cc4ab91073d2ac7404ad146139f86ecee7193
- https://git.kernel.org/stable/c/5de7513f38f3c19c0610294ee478242bea356f8c
- https://git.kernel.org/stable/c/97b8c5d322c5c0038cac4bc56fdbe237d0be426f
- https://git.kernel.org/stable/c/b7dcda76fd0615c0599c89f36873a6cd48e02dbb
- https://git.kernel.org/stable/c/de9c4861fb42f0cd72da844c3c34f692d5895b7b
- https://git.kernel.org/stable/c/ea99b88b1999ebcb24d5d3a6b7910030f40d3bba
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38574.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
