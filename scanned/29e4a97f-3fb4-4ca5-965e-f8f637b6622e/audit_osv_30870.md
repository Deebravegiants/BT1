# [M] tipc: fix NULL deref in cleanup_bearer()

## Summary
Severity: Medium
Advisory: CVE-2024-56661
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56661
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.287 <5.4.288, >=5.10.231 <5.10.232, >=5.15.174 <5.15.175, >=6.1.120 <6.1.121, >=6.6.66 <6.6.67, >=6.12.5 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix NULL deref in cleanup_bearer()

syzbot found [1] that after blamed commit, ub->ubsock->sk
was NULL when attempting the atomic_dec() :

atomic_dec(&tipc_net(sock_net(ub->ubsock->sk))->wq_count);

Fix this by caching the tipc_net pointer.

[1]

Oops: general protection fault, probably for non-canonical address 0xdffffc0000000006: 0000 [#1] PREEMPT SMP KASAN PTI
KASAN: null-ptr-deref in range [0x0000000000000030-0x0000000000000037]
CPU: 0 UID: 0 PID: 5896 Comm: kworker/0:3 Not tainted 6.13.0-rc1-next-20241203-syzkaller #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
Workqueue: events cleanup_bearer
 RIP: 0010:read_pnet include/net/net_namespace.h:387 [inline]
 RIP: 0010:sock_net include/net/sock.h:655 [inline]
 RIP: 0010:cleanup_bearer+0x1f7/0x280 net/tipc/udp_media.c:820
Code: 18 48 89 d8 48 c1 e8 03 42 80 3c 28 00 74 08 48 89 df e8 3c f7 99 f6 48 8b 1b 48 83 c3 30 e8 f0 e4 60 00 48 89 d8 48 c1 e8 03 <42> 80 3c 28 00 74 08 48 89 df e8 1a f7 99 f6 49 83 c7 e8 48 8b 1b
RSP: 0018:ffffc9000410fb70 EFLAGS: 00010206
RAX: 0000000000000006 RBX: 0000000000000030 RCX: ffff88802fe45a00
RDX: 0000000000000001 RSI: 0000000000000008 RDI: ffffc9000410f900
RBP: ffff88807e1f0908 R08: ffffc9000410f907 R09: 1ffff92000821f20
R10: dffffc0000000000 R11: fffff52000821f21 R12: ffff888031d19980
R13: dffffc0000000000 R14: dffffc0000000000 R15: ffff88807e1f0918
FS:  0000000000000000(0000) GS:ffff8880b8600000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000556ca050b000 CR3: 0000000031c0c000 CR4: 00000000003526f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400

## References
- https://git.kernel.org/stable/c/07b569eda6fe6a1e83be5a587abee12d1303f95e
- https://git.kernel.org/stable/c/754ec823ee53422361da7958a8c8bf3275426912
- https://git.kernel.org/stable/c/89ecda492d0a37fd00aaffc4151f1f44c26d93ac
- https://git.kernel.org/stable/c/a771f349c95d3397636861a0a6462d4a7a7ecb25
- https://git.kernel.org/stable/c/a852c82eda4991e21610837aaa160965be71f5cc
- https://git.kernel.org/stable/c/b04d86fff66b15c07505d226431f808c15b1703c
- https://git.kernel.org/stable/c/d1d4dfb189a115734bff81c411bc58d9e348db7d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56661.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
