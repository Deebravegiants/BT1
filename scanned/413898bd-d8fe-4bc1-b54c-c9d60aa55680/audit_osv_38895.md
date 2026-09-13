# [H] bpf: sockmap: Fix use-after-free of sk->sk_socket in sk_psock_verdict_data_ready().

## Summary
Severity: High
Advisory: CVE-2026-43016
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43016
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: sockmap: Fix use-after-free of sk->sk_socket in sk_psock_verdict_data_ready().

syzbot reported use-after-free of AF_UNIX socket's sk->sk_socket
in sk_psock_verdict_data_ready(). [0]

In unix_stream_sendmsg(), the peer socket's ->sk_data_ready() is
called after dropping its unix_state_lock().

Although the sender socket holds the peer's refcount, it does not
prevent the peer's sock_orphan(), and the peer's sk_socket might
be freed after one RCU grace period.

Let's fetch the peer's sk->sk_socket and sk->sk_socket->ops under
RCU in sk_psock_verdict_data_ready().

[0]:
BUG: KASAN: slab-use-after-free in sk_psock_verdict_data_ready+0xec/0x590 net/core/skmsg.c:1278
Read of size 8 at addr ffff8880594da860 by task syz.4.1842/11013

CPU: 1 UID: 0 PID: 11013 Comm: syz.4.1842 Not tainted syzkaller #0 PREEMPT(full)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 02/12/2026
Call Trace:
 <TASK>
 dump_stack_lvl+0xe8/0x150 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0xba/0x230 mm/kasan/report.c:482
 kasan_report+0x117/0x150 mm/kasan/report.c:595
 sk_psock_verdict_data_ready+0xec/0x590 net/core/skmsg.c:1278
 unix_stream_sendmsg+0x8a3/0xe80 net/unix/af_unix.c:2482
 sock_sendmsg_nosec net/socket.c:721 [inline]
 __sock_sendmsg net/socket.c:736 [inline]
 ____sys_sendmsg+0x972/0x9f0 net/socket.c:2585
 ___sys_sendmsg+0x2a5/0x360 net/socket.c:2639
 __sys_sendmsg net/socket.c:2671 [inline]
 __do_sys_sendmsg net/socket.c:2676 [inline]
 __se_sys_sendmsg net/socket.c:2674 [inline]
 __x64_sys_sendmsg+0x1bd/0x2a0 net/socket.c:2674
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0x14d/0xf80 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
RIP: 0033:0x7facf899c819
Code: ff c3 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 44 00 00 48 89 f8 48 89 f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 c7 c1 e8 ff ff ff f7 d8 64 89 01 48
RSP: 002b:00007facf9827028 EFLAGS: 00000246 ORIG_RAX: 000000000000002e
RAX: ffffffffffffffda RBX: 00007facf8c15fa0 RCX: 00007facf899c819
RDX: 0000000000000000 RSI: 0000200000000500 RDI: 0000000000000004
RBP: 00007facf8a32c91 R08: 0000000000000000 R09: 0000000000000000
R10: 0000000000000000 R11: 0000000000000246 R12: 0000000000000000
R13: 00007facf8c16038 R14: 00007facf8c15fa0 R15: 00007ffd41b01c78
 </TASK>

Allocated by task 11013:
 kasan_save_stack mm/kasan/common.c:57 [inline]
 kasan_save_track+0x3e/0x80 mm/kasan/common.c:78
 unpoison_slab_object mm/kasan/common.c:340 [inline]
 __kasan_slab_alloc+0x6c/0x80 mm/kasan/common.c:366
 kasan_slab_alloc include/linux/kasan.h:253 [inline]
 slab_post_alloc_hook mm/slub.c:4538 [inline]
 slab_alloc_node mm/slub.c:4866 [inline]
 kmem_cache_alloc_lru_noprof+0x2b8/0x640 mm/slub.c:4885
 sock_alloc_inode+0x28/0xc0 net/socket.c:316
 alloc_inode+0x6a/0x1b0 fs/inode.c:347
 new_inode_pseudo include/linux/fs.h:3003 [inline]
 sock_alloc net/socket.c:631 [inline]
 __sock_create+0x12d/0x9d0 net/socket.c:1562
 sock_create net/socket.c:1656 [inline]
 __sys_socketpair+0x1c4/0x560 net/socket.c:1803
 __do_sys_socketpair net/socket.c:1856 [inline]
 __se_sys_socketpair net/socket.c:1853 [inline]
 __x64_sys_socketpair+0x9b/0xb0 net/socket.c:1853
 do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
 do_syscall_64+0x14d/0xf80 arch/x86/entry/syscall_64.c:94
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Freed by task 15:
 kasan_save_stack mm/kasan/common.c:57 [inline]
 kasan_save_track+0x3e/0x80 mm/kasan/common.c:78
 kasan_save_free_info+0x46/0x50 mm/kasan/generic.c:584
 poison_slab_object mm/kasan/common.c:253 [inline]
 __kasan_slab_free+0x5c/0x80 mm/kasan/common.c:285
 kasan_slab_free include/linux/kasan.h:235 [inline]
 slab_free_hook mm/slub.c:2685 [inline]
 slab_free mm/slub.c:6165 [inline]
 kmem_cache_free+0x187/0x630 mm/slub.c:6295
 rcu_do_batch kernel/rcu/tree.c:
---truncated---

## References
- https://git.kernel.org/stable/c/18861f87a043e78b1f901cae4237e755ed7ef095
- https://git.kernel.org/stable/c/68187f18a89be4b6237d28ae1313b5adf76238c6
- https://git.kernel.org/stable/c/8d597e3e74027900ffa81b8ff47ab51999a3e110
- https://git.kernel.org/stable/c/ad8391d37f334ee73ba91926f8b4e4cf6d31ea04
- https://git.kernel.org/stable/c/af95bc39a83d82ae6ad253986335037256888b3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43016.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
