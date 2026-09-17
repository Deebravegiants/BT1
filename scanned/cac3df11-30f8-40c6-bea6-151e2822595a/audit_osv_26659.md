# [H] mptcp: fix disconnect vs accept race

## Summary
Severity: High
Advisory: CVE-2023-53490
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53490
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix disconnect vs accept race

Despite commit 0ad529d9fd2b ("mptcp: fix possible divide by zero in
recvmsg()"), the mptcp protocol is still prone to a race between
disconnect() (or shutdown) and accept.

The root cause is that the mentioned commit checks the msk-level
flag, but mptcp_stream_accept() does acquire the msk-level lock,
as it can rely directly on the first subflow lock.

As reported by Christoph than can lead to a race where an msk
socket is accepted after that mptcp_subflow_queue_clean() releases
the listener socket lock and just before it takes destructive
actions leading to the following splat:

BUG: kernel NULL pointer dereference, address: 0000000000000012
PGD 5a4ca067 P4D 5a4ca067 PUD 37d4c067 PMD 0
Oops: 0000 [#1] PREEMPT SMP
CPU: 2 PID: 10955 Comm: syz-executor.5 Not tainted 6.5.0-rc1-gdc7b257ee5dd #37
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.11.0-2.el7 04/01/2014
RIP: 0010:mptcp_stream_accept+0x1ee/0x2f0 include/net/inet_sock.h:330
Code: 0a 09 00 48 8b 1b 4c 39 e3 74 07 e8 bc 7c 7f fe eb a1 e8 b5 7c 7f fe 4c 8b 6c 24 08 eb 05 e8 a9 7c 7f fe 49 8b 85 d8 09 00 00 <0f> b6 40 12 88 44 24 07 0f b6 6c 24 07 bf 07 00 00 00 89 ee e8 89
RSP: 0018:ffffc90000d07dc0 EFLAGS: 00010293
RAX: 0000000000000000 RBX: ffff888037e8d020 RCX: ffff88803b093300
RDX: 0000000000000000 RSI: ffffffff833822c5 RDI: ffffffff8333896a
RBP: 0000607f82031520 R08: ffff88803b093300 R09: 0000000000000000
R10: 0000000000000000 R11: 0000000000003e83 R12: ffff888037e8d020
R13: ffff888037e8c680 R14: ffff888009af7900 R15: ffff888009af6880
FS:  00007fc26d708640(0000) GS:ffff88807dd00000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000000000000012 CR3: 0000000066bc5001 CR4: 0000000000370ee0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
 do_accept+0x1ae/0x260 net/socket.c:1872
 __sys_accept4+0x9b/0x110 net/socket.c:1913
 __do_sys_accept4 net/socket.c:1954 [inline]
 __se_sys_accept4 net/socket.c:1951 [inline]
 __x64_sys_accept4+0x20/0x30 net/socket.c:1951
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x47/0xa0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x6e/0xd8

Address the issue by temporary removing the pending request socket
from the accept queue, so that racing accept() can't touch them.

After depleting the msk - the ssk still exists, as plain TCP sockets,
re-insert them into the accept queue, so that later inet_csk_listen_stop()
will complete the tcp socket disposal.

## References
- https://git.kernel.org/stable/c/511b90e39250135a7f900f1c3afbce25543018a2
- https://git.kernel.org/stable/c/b2b4c84eb7149f34c0f25f17042d095ba5357d68
- https://git.kernel.org/stable/c/ded9f5551ce5cafa3c41c794428c27a0d0a00542
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53490.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
